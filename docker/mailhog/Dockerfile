FROM mailhog/mailhog:latest AS binary_source

FROM debian:bookworm-slim

# Install necessary dependencies
RUN apt update && apt install -y dos2unix bash && apt clean

COPY --from=binary_source /usr/local/bin/MailHog /usr/local/bin/MailHog

COPY commands/setup_mailhog_auth.sh /commands/setup_mailhog_auth.sh

RUN dos2unix /commands/setup_mailhog_auth.sh && chmod +x /commands/setup_mailhog_auth.sh

EXPOSE 1025 8025
