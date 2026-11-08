FROM cgr.dev/chainguard/minio:latest AS minio

FROM alpine:3.22

RUN apk add --no-cache ca-certificates curl

COPY --from=minio /usr/bin/minio /usr/bin/minio

USER 65532:65532

EXPOSE 9000 9001

ENTRYPOINT ["/usr/bin/minio"]
CMD ["server", "--console-address", ":9001", "/data"]