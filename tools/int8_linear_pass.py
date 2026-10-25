"""Candidate-only adaptation for the pinned exporter's folded-transpose bug.

No installed source is modified. Only the INT8 worker's builder binding changes.
The conservative upstream transform requires an explicit two-dimensional
transpose; source-partition reconstruction cannot safely infer a folded one.
"""

import hashlib
from pathlib import Path


PINNED_SOURCES = {
    "backends/xnnpack/_passes/convert_to_linear.py":
        "475df30d1f044acea482f12d968a17a1dfc1701456819757135cbd28d89769f3",
    "backends/transforms/addmm_mm_to_linear.py":
        "a6dc5fc5349600b5dda5c41d5f6a464da56569c9dac5184a3f3ffed44349de07",
    "extension/llm/export/builder.py":
        "d7944d05e758e3d166055366cf157c56151514018c40c30653ea9a3a7a283343",
}


def conservative_linear_pass():
    from executorch.backends.transforms.addmm_mm_to_linear import (
        apply_addmm_mm_to_linear_transform,
    )
    from executorch.exir.dialects._ops import ops
    from executorch.exir.pass_base import ExportPass

    class ConservativeLinearPass(ExportPass):
        def call(self, graph_module):
            graph_module.graph.lint()
            for node in graph_module.graph.nodes:
                if node.op != "call_function" or node.target not in (
                    ops.edge.aten.mm.default, ops.edge.aten.addmm.default
                ):
                    continue
                is_addmm = node.target == ops.edge.aten.addmm.default
                rhs = node.args[2 if is_addmm else 1]
                if rhs.target not in (
                    ops.edge.aten.t_copy.default, ops.edge.aten.permute_copy.default
                ):
                    continue  # Already-folded or independent MM remains untouched.
                value = rhs.args[0].meta.get("val")
                if value is None or value.dim() != 2:
                    raise ValueError("unsupported_linear_transpose")
                if rhs.target == ops.edge.aten.permute_copy.default:
                    if len(rhs.args) != 2 or list(rhs.args[1]) != [1, 0]:
                        raise ValueError("unsupported_linear_permutation")
                if is_addmm and (
                    len(node.args) != 3
                    or any(key not in ("alpha", "beta") for key in node.kwargs)
                    or node.kwargs.get("alpha", 1) != 1
                    or node.kwargs.get("beta", 1) != 1
                ):
                    raise ValueError("unsupported_linear_addmm_scaling")
            graph_module.graph = apply_addmm_mm_to_linear_transform(graph_module.graph)
            graph_module.graph.lint()
            graph_module.recompile()
            result = super().call(graph_module)
            result.graph_module.graph.lint()
            return result

    return ConservativeLinearPass


def install_candidate_pass():
    from executorch.extension.llm.export import builder

    package = Path(builder.__file__).resolve().parents[3]
    records = []
    for relative, expected in PINNED_SOURCES.items():
        actual = hashlib.sha256((package / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError("candidate_linear_pass_source_mismatch")
        records.append({"path": relative, "sha256": actual})
    builder.ConvertToLinearPass = conservative_linear_pass()
    return {
        "adaptation": "explicit_2d_transpose_only_no_source_partition_reconstruction",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "upstream_sources": records,
        "installed_sources_modified": False,
    }
