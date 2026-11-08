FROM nginx:alpine

RUN apk add --no-cache \
    apache2-utils \
    dos2unix \
    bash

COPY ./commands/set_nginx_basic_auth.sh /commands/set_nginx_basic_auth.sh

RUN dos2unix /commands/set_nginx_basic_auth.sh \
    && chmod +x /commands/set_nginx_basic_auth.sh

ENTRYPOINT ["/commands/set_nginx_basic_auth.sh"]

CMD ["nginx", "-g", "daemon off;"]