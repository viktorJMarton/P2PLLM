//! Bounded, public-fixture-only protocol laboratory.
//!
//! This state machine does not authenticate peers. The TCP adapter is restricted
//! to loopback and must never be used for personal-derived requests.

use std::collections::HashMap;

pub const MAX_FRAME_BYTES: usize = 256;
pub const MAX_TASK_IDS: usize = 64;
pub const MAX_INPUT: u64 = 1_000_000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum TaskState {
    Completed(u64),
    Cancelled,
}

#[derive(Debug, Clone, Copy)]
struct Task {
    input: Option<u64>,
    state: TaskState,
}

/// State belongs to one TCP connection. Closing it expires all cached results.
#[derive(Default)]
pub struct LabSession {
    hello_seen: bool,
    tasks: HashMap<String, Task>,
}

pub struct Response {
    pub line: String,
    pub close: bool,
}

impl Response {
    fn ok(line: String) -> Self {
        Self { line, close: false }
    }

    fn error(code: &'static str, close: bool) -> Self {
        Self {
            line: format!("P2P1 ERROR {code}\n"),
            close,
        }
    }
}

fn valid_id(id: &str) -> bool {
    !id.is_empty()
        && id.len() <= 32
        && id
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-')
}

impl LabSession {
    pub fn handle(&mut self, bytes: &[u8]) -> Response {
        if bytes.len() > MAX_FRAME_BYTES || bytes.last() != Some(&b'\n') {
            return Response::error("RESOURCE_LIMIT", true);
        }
        let Ok(frame) = std::str::from_utf8(&bytes[..bytes.len() - 1]) else {
            return Response::error("RESOURCE_LIMIT", true);
        };
        let parts: Vec<_> = frame.split(' ').collect();
        if parts.first().is_none_or(|part| *part != "P2P1") {
            return Response::error("VERSION_UNSUPPORTED", true);
        }
        if !self.hello_seen {
            if parts.len() == 3 && parts[1] == "HELLO" && valid_id(parts[2]) {
                self.hello_seen = true;
                return Response::ok("P2P1 HELLO lab-peer\n".to_owned());
            }
            return Response::error("OPERATION_UNSUPPORTED", true);
        }
        match parts.as_slice() {
            ["P2P1", "OFFER", task_id, "SQUARE", value] => self.offer(task_id, value),
            ["P2P1", "CANCEL", task_id] => self.cancel(task_id),
            _ => Response::error("OPERATION_UNSUPPORTED", false),
        }
    }

    fn offer(&mut self, task_id: &str, value: &str) -> Response {
        if !valid_id(task_id) {
            return Response::error("OPERATION_UNSUPPORTED", false);
        }
        // Canonical decimal representation makes duplicate identity unambiguous.
        let Ok(input) = value.parse::<u64>() else {
            return Response::error("OPERATION_UNSUPPORTED", false);
        };
        if input.to_string() != value || input > MAX_INPUT {
            return Response::error("RESOURCE_LIMIT", false);
        }
        if let Some(existing) = self.tasks.get(task_id) {
            if existing.input.is_some_and(|old| old != input) {
                return Response::error("STEP_CONFLICT", false);
            }
            return match existing.state {
                TaskState::Completed(output) => {
                    Response::ok(format!("P2P1 RESULT {task_id} {output}\n"))
                }
                TaskState::Cancelled => Response::ok(format!("P2P1 CANCELLED {task_id}\n")),
            };
        }
        if self.tasks.len() >= MAX_TASK_IDS {
            return Response::error("RESOURCE_LIMIT", false);
        }
        let Some(output) = input.checked_mul(input) else {
            return Response::error("RESOURCE_LIMIT", false);
        };
        self.tasks.insert(
            (*task_id).to_owned(),
            Task {
                input: Some(input),
                state: TaskState::Completed(output),
            },
        );
        Response::ok(format!("P2P1 RESULT {task_id} {output}\n"))
    }

    fn cancel(&mut self, task_id: &str) -> Response {
        if !valid_id(task_id) {
            return Response::error("OPERATION_UNSUPPORTED", false);
        }
        if !self.tasks.contains_key(task_id) && self.tasks.len() >= MAX_TASK_IDS {
            return Response::error("RESOURCE_LIMIT", false);
        }
        self.tasks
            .entry((*task_id).to_owned())
            .and_modify(|task| task.state = TaskState::Cancelled)
            .or_insert(Task {
                input: None,
                state: TaskState::Cancelled,
            });
        Response::ok(format!("P2P1 CANCELLED {task_id}\n"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn call(session: &mut LabSession, line: &str) -> Response {
        session.handle(line.as_bytes())
    }

    #[test]
    fn handshake_is_required_and_version_is_rejected() {
        let mut session = LabSession::default();
        assert_eq!(
            call(&mut session, "P2P1 OFFER a SQUARE 2\n").line,
            "P2P1 ERROR OPERATION_UNSUPPORTED\n"
        );
        assert!(call(&mut session, "P2P2 HELLO client\n").close);
        assert_eq!(
            call(&mut session, "P2P1 HELLO client\n").line,
            "P2P1 HELLO lab-peer\n"
        );
    }

    #[test]
    fn replay_conflict_and_cancellation_are_bounded_to_session() {
        let mut session = LabSession::default();
        call(&mut session, "P2P1 HELLO client\n");
        assert_eq!(
            call(&mut session, "P2P1 OFFER a SQUARE 12\n").line,
            "P2P1 RESULT a 144\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 OFFER a SQUARE 12\n").line,
            "P2P1 RESULT a 144\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 OFFER a SQUARE 13\n").line,
            "P2P1 ERROR STEP_CONFLICT\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 CANCEL a\n").line,
            "P2P1 CANCELLED a\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 OFFER a SQUARE 12\n").line,
            "P2P1 CANCELLED a\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 CANCEL b\n").line,
            "P2P1 CANCELLED b\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 OFFER b SQUARE 1\n").line,
            "P2P1 CANCELLED b\n"
        );
        let mut fresh = LabSession::default();
        call(&mut fresh, "P2P1 HELLO client\n");
        assert_eq!(
            call(&mut fresh, "P2P1 OFFER a SQUARE 13\n").line,
            "P2P1 RESULT a 169\n"
        );
    }

    #[test]
    fn malformed_and_resource_limits() {
        let mut session = LabSession::default();
        assert!(session.handle(&vec![b'A'; MAX_FRAME_BYTES + 1]).close);
        assert!(session.handle(&[0xff, b'\n']).close);
        call(&mut session, "P2P1 HELLO client\n");
        assert_eq!(
            call(&mut session, "P2P1 OFFER x SQUARE 1000001\n").line,
            "P2P1 ERROR RESOURCE_LIMIT\n"
        );
        assert_eq!(
            call(&mut session, "P2P1 OFFER x SQUARE 01\n").line,
            "P2P1 ERROR RESOURCE_LIMIT\n"
        );
        for i in 0..MAX_TASK_IDS {
            assert!(call(&mut session, &format!("P2P1 OFFER t{i} SQUARE 1\n"))
                .line
                .starts_with("P2P1 RESULT"));
        }
        assert_eq!(
            call(&mut session, "P2P1 OFFER overflow SQUARE 1\n").line,
            "P2P1 ERROR RESOURCE_LIMIT\n"
        );
    }
}
