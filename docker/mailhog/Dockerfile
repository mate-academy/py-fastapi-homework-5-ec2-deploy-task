FROM golang:latest

RUN apt-get update && apt-get install -y \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

RUN go install github.com/mailhog/MailHog@latest

ENV PATH="/go/bin:$PATH"

COPY commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh

EXPOSE 1025 8025