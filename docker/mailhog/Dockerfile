FROM golang:1.24.1- AS builder
RUN go install github.com/mailhog/MailHog@v1.0.1

FROM debian:bookworm-slim

# Install necessary dependencies
RUN apt update && apt install -y  \
    wget \
    dos2unix \
    && apt clean

# Add Go's bin directory to the PATH to make MailHog executable globally

COPY --from=builder /go/bin/MailHog /usr/local/bin/mailhog

# Copy the commands directory into the container
COPY commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

# Ensure all scripts in the commands directory have Unix-style line endings and are executable
RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh
