Test-only TLS material for the loopback asset server (127.0.0.1, ::1/localhost).
bench-ca.pem is trusted only by the three benchmark apps (network security config);
its private key was discarded after signing server.pem. Regenerate both with openssl if needed.
