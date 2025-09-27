FROM --platform=linux/amd64 openjdk:25-bookworm
ADD entrypoint.sh /

RUN apt update && apt install -y unzip xdelta3 && mkdir -p /app && chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
