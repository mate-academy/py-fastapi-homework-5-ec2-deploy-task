FROM debian:bookworm-slim

# Install necessary dependencies
RUN apt-get update && apt-get install -y  \
    wget \
    dos2unix \
    && apt-get clean

# Install MailHog using Go
RUN wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64 -O /usr/local/bin/mailhog \
    && chmod +x /usr/local/bin/mailhog

# Copy the commands directory into the container
COPY commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

# Ensure all scripts in the commands directory have Unix-style line endings and are executable
RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh
