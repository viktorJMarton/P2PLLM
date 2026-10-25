//! Manual public-fixture client for the loopback protocol laboratory.

use p2p_protocol_session::{MAX_FRAME_BYTES, MAX_INPUT};
use std::io::{self, Read, Write};
use std::net::{Ipv4Addr, SocketAddr, TcpStream};
use std::time::{Duration, Instant};

fn invalid(message: &'static str) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidInput, message)
}

fn read_frame(stream: &mut TcpStream) -> io::Result<String> {
    let mut bytes = Vec::with_capacity(32);
    let mut byte = [0u8; 1];
    let deadline = Instant::now() + Duration::from_secs(10);
    loop {
        let remaining = deadline.saturating_duration_since(Instant::now());
        if remaining.is_zero() {
            return Err(io::Error::new(io::ErrorKind::TimedOut, "response deadline"));
        }
        stream.set_read_timeout(Some(remaining.min(Duration::from_secs(5))))?;
        if stream.read(&mut byte)? == 0 {
            return Err(io::Error::new(
                io::ErrorKind::UnexpectedEof,
                "partial response",
            ));
        }
        bytes.push(byte[0]);
        if bytes.len() > MAX_FRAME_BYTES {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "response too long",
            ));
        }
        if byte[0] == b'\n' {
            return String::from_utf8(bytes)
                .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "non-UTF-8 response"));
        }
    }
}

fn run() -> io::Result<()> {
    let mut args = std::env::args().skip(1);
    let address = args
        .next()
        .ok_or_else(|| invalid("usage: p2p-lab-client 127.0.0.1:PORT N"))?;
    let number = args
        .next()
        .ok_or_else(|| invalid("usage: p2p-lab-client 127.0.0.1:PORT N"))?;
    if args.next().is_some() {
        return Err(invalid("expected exactly an address and a number"));
    }
    let address: SocketAddr = address.parse().map_err(|_| invalid("invalid address"))?;
    if address.ip() != Ipv4Addr::LOCALHOST {
        return Err(invalid("loopback only"));
    }
    let value: u64 = number.parse().map_err(|_| invalid("invalid number"))?;
    if number != value.to_string() || value > MAX_INPUT {
        return Err(invalid("number must be canonical decimal in 0..=1000000"));
    }

    let mut stream = TcpStream::connect_timeout(&address, Duration::from_secs(5))?;
    stream.set_read_timeout(Some(Duration::from_secs(5)))?;
    stream.set_write_timeout(Some(Duration::from_secs(5)))?;
    stream.write_all(b"P2P1 HELLO desktop-cli\n")?;
    if read_frame(&mut stream)? != "P2P1 HELLO lab-peer\n" {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "unexpected handshake",
        ));
    }
    stream.write_all(format!("P2P1 OFFER demo SQUARE {value}\n").as_bytes())?;
    let expected = format!("P2P1 RESULT demo {}\n", value * value);
    if read_frame(&mut stream)? != expected {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "unexpected result",
        ));
    }
    println!("{}", value * value);
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("p2p-lab-client: {error}");
        std::process::exit(1);
    }
}
