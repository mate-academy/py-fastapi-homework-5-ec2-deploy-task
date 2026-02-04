FROM golang:bookworm

# Install necessary dependencies
RUN apt update && apt install -y  \
    wget \
    curl \
    dos2unix \
    && apt clean

# Install MailHog using Go
RUN wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64 \
    && mv MailHog_linux_amd64 /usr/local/bin/MailHog \
    && chmod +x /usr/local/bin/MailHog

RUN mkdir -p /root/go/bin && ln -s /usr/local/bin/MailHog /root/go/bin/MailHog

# Copy the commands directory into the container
COPY commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

# Ensure all scripts in the commands directory have Unix-style line endings and are executable
RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh