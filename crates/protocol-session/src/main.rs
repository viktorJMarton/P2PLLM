//! Local synthetic test peer. Plain TCP provides no peer authentication/privacy.

use p2p_protocol_session::{LabSession, MAX_FRAME_BYTES};
use std::io::{self, Read, Write};
use std::net::{Ipv4Addr, SocketAddr, TcpListener, TcpStream};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

const MAX_ACTIVE_CONNECTIONS: usize = 8;
const MAX_FRAMES_PER_SESSION: usize = 256;
const SESSION_DURATION: Duration = Duration::from_secs(30);

struct ActiveConnection(Arc<AtomicUsize>);

impl Drop for ActiveConnection {
    fn drop(&mut self) {
        self.0.fetch_sub(1, Ordering::AcqRel);
    }
}

fn read_frame(stream: &mut TcpStream, deadline: Instant) -> io::Result<Option<Vec<u8>>> {
    let mut frame = Vec::with_capacity(MAX_FRAME_BYTES);
    let mut byte = [0u8; 1];
    loop {
        let remaining = deadline.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            return Err(io::Error::new(io::ErrorKind::TimedOut, "session deadline"));
        }
        stream.set_read_timeout(Some(remaining.min(Duration::from_secs(5))))?;
        match stream.read(&mut byte) {
            Ok(0) if frame.is_empty() => return Ok(None),
            Ok(0) => {
                return Err(io::Error::new(
                    io::ErrorKind::UnexpectedEof,
                    "partial frame",
                ))
            }
            Ok(_) => {
                frame.push(byte[0]);
                if byte[0] == b'\n' {
                    return Ok(Some(frame));
                }
                if frame.len() == MAX_FRAME_BYTES {
                    return Ok(Some(frame));
                }
            }
            Err(error) => return Err(error),
        }
    }
}

fn serve_connection(mut stream: TcpStream) -> io::Result<()> {
    stream.set_write_timeout(Some(Duration::from_secs(5)))?;
    let mut session = LabSession::default();
    let deadline = Instant::now() + SESSION_DURATION;
    let mut frames = 0usize;
    loop {
        let Some(frame) = read_frame(&mut stream, deadline)? else {
            return Ok(());
        };
        if frames >= MAX_FRAMES_PER_SESSION {
            stream.write_all(b"P2P1 ERROR RESOURCE_LIMIT\n")?;
            return Ok(());
        }
        frames += 1;
        let response = session.handle(&frame);
        stream.write_all(response.line.as_bytes())?;
        if response.close {
            return Ok(());
        }
    }
}

fn main() -> io::Result<()> {
    let requested = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "127.0.0.1:0".to_owned());
    if std::env::args().count() > 2 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "one bind address expected",
        ));
    }
    let addr: SocketAddr = requested
        .parse()
        .map_err(|_| io::Error::new(io::ErrorKind::InvalidInput, "invalid bind address"))?;
    if addr.ip() != Ipv4Addr::LOCALHOST {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "loopback only",
        ));
    }
    let listener = TcpListener::bind(addr)?;
    let active = Arc::new(AtomicUsize::new(0));
    println!("LISTEN {}", listener.local_addr()?);
    io::stdout().flush()?;
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if active
                    .fetch_update(Ordering::AcqRel, Ordering::Acquire, |count| {
                        (count < MAX_ACTIVE_CONNECTIONS).then_some(count + 1)
                    })
                    .is_err()
                {
                    // Over-cap clients receive no protocol response or worker.
                    drop(stream);
                    continue;
                }
                let worker_count = Arc::clone(&active);
                if let Err(error) = thread::Builder::new().spawn(move || {
                    let _slot = ActiveConnection(worker_count);
                    let _ = serve_connection(stream);
                }) {
                    active.fetch_sub(1, Ordering::AcqRel);
                    return Err(error);
                }
            }
            Err(error) => return Err(error),
        }
    }
    Ok(())
}
