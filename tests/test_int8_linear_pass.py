"""Synthetic numerical checks, executed in the pinned export venv.

The standard host suite can lack the optional model-export dependencies.
Run this file with that venv before executing an INT8 candidate export.
"""

import copy
import unittest

from tools.export_qwen import install_logging_guard
from tools.int8_linear_pass import conservative_linear_pass, install_candidate_pass


class LinearAdaptationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_logging_guard()
        try:
            import torch
            from executorch.exir.dialects._ops import ops
        except ModuleNotFoundError:
            raise unittest.SkipTest("Requires pinned optional export venv")
        cls.torch, cls.ops = torch, ops

    def fixture(self, explicit, bias=False, permutation=False, kwargs=None):
        torch, ops = self.torch, self.ops
        graph = torch.fx.Graph()
        x, w = graph.placeholder("x"), graph.placeholder("weight")
        xv = torch.arange(6, dtype=torch.float32).reshape(2, 3)
        wv = torch.arange(15, dtype=torch.float32).reshape((5, 3) if explicit else (3, 5))
        x.meta["val"], w.meta["val"] = xv, wv
        rhs = w
        if explicit:
            target = ops.edge.aten.permute_copy.default if permutation else ops.edge.aten.t_copy.default
            rhs = graph.call_function(target, (w, [1, 0]) if permutation else (w,))
            rhs.meta["val"] = wv.t().contiguous()
        args = [xv, wv]
        if bias:
            b = graph.placeholder("bias")
            bv = torch.arange(5, dtype=torch.float32)
            b.meta["val"] = bv
            args.append(bv)
            result = graph.call_function(ops.edge.aten.addmm.default, (b, x, rhs), kwargs or {})
        else:
            result = graph.call_function(ops.edge.aten.mm.default, (x, rhs))
        result.meta["val"] = xv @ (wv.t() if explicit else wv) + (args[2] if bias else 0)
        result.meta["source_fn_stack"] = [("linear", torch.nn.functional.linear)]
        graph.output(result)
        return torch.fx.GraphModule({}, graph), args

    def test_folded_explicit_and_biased_outputs_with_varying_batch(self):
        for explicit, bias, permutation in (
            (False, False, False), (False, True, False),
            (True, False, False), (True, True, False),
            (True, False, True), (True, True, True),
        ):
            with self.subTest(explicit=explicit, bias=bias, permutation=permutation):
                original, args = self.fixture(explicit, bias, permutation)
                transformed = conservative_linear_pass()()(copy.deepcopy(original)).graph_module
                linear_count = sum(n.target == self.ops.edge.aten.linear.default for n in transformed.graph.nodes)
                self.assertEqual(linear_count, int(explicit))
                for batch in (1, 2, 4):
                    args[0] = self.torch.arange(batch * 3, dtype=self.torch.float32).reshape(batch, 3)
                    expected, actual = original(*args), transformed(*args)
                    self.assertEqual(tuple(actual.shape), (batch, 5))
                    self.assertTrue(self.torch.equal(actual, expected), "Synthetic output differs")

    def test_original_pass_reproduces_rectangular_failure(self):
        from executorch.backends.xnnpack._passes.convert_to_linear import ConvertToLinearPass
        original, _ = self.fixture(False)
        with self.assertRaises(RuntimeError):
            ConvertToLinearPass()(original)

    def test_scaled_addmm_is_rejected(self):
        for kwargs in ({"alpha": 2}, {"beta": 0}):
            original, _ = self.fixture(True, bias=True, kwargs=kwargs)
            with self.assertRaisesRegex(ValueError, "unsupported_linear_addmm_scaling"):
                conservative_linear_pass()()(original)

    def test_non_transpose_permutation_is_rejected(self):
        original, _ = self.fixture(True, permutation=True)
        for node in original.graph.nodes:
            if node.target == self.ops.edge.aten.permute_copy.default:
                node.args = (node.args[0], [0, 1])
        with self.assertRaisesRegex(ValueError, "unsupported_linear_permutation"):
            conservative_linear_pass()()(original)

    def test_install_is_in_memory_and_records_pinned_sources(self):
        from executorch.extension.llm.export import builder
        before = builder.ConvertToLinearPass
        try:
            receipt = install_candidate_pass()
            self.assertEqual(len(receipt["upstream_sources"]), 3)
            self.assertFalse(receipt["installed_sources_modified"])
            self.assertIsNot(builder.ConvertToLinearPass, before)
        finally:
            builder.ConvertToLinearPass = before


if __name__ == "__main__":
    unittest.main()
