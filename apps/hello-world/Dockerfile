# Optional packaging exercise. Not used by local checks or the platform.
FROM nginx/nginx-unprivileged:stable-alpine@sha256:0c53a1f2890c3526bfd201440f0fd3970e5b78f80630f58284aad0d34b5ec7bd
LABEL org.opencontainers.image.title="OpenOps Hello World"
COPY public/ /usr/share/nginx/html/
EXPOSE 8080
