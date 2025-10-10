FROM golang:1.24-bullseye AS builder

# Set Go bin path
ENV PATH="/go/bin:$PATH"

# Install dos2unix for script conversion
RUN apt-get update && apt-get install -y dos2unix && apt-get clean

# Copy setup script
COPY commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

# Convert to Unix line endings and make executable
RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh

# Install MailHog using Go
RUN go install github.com/mailhog/MailHog@latest

# ----------------------------
# Create minimal runtime image
FROM debian:bookworm-slim

# Install bash
RUN apt-get update && apt-get install -y bash && apt-get clean

# Copy MailHog binary from builder
COPY --from=builder /go/bin/MailHog /usr/local/bin/MailHog

# Copy setup script
COPY --from=builder /commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

# Ensure executable
RUN chmod +x /commands/setup_mailhog_auth.sh

# Set PATH
ENV PATH="/usr/local/bin:$PATH"

# Default command (can be overridden in docker-compose)
CMD ["/bin/bash", "-c", "/commands/setup_mailhog_auth.sh && MailHog"]
