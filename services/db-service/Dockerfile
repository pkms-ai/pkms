FROM rust:1.74-slim as builder

WORKDIR /usr/src/

# Copy only Cargo files first to cache dependencies
COPY Cargo.toml Cargo.lock ./
COPY migration ./migration

# Create a temporary dummy main.rs file to compile dependencies only
RUN mkdir -p src/bin && echo "fn main() {}" > src/bin/main.rs

# Compile dependencies only
RUN cargo build --release -j 4 --bin db_service-cli

# Now remove the dummy file and copy the rest of the source code
RUN rm -rf src

# Now copy the rest of the source code
COPY src ./src
COPY config ./config

# or
# COPY . .

RUN cargo build --release -j 4

FROM debian:bookworm-slim

WORKDIR /usr/app

COPY --from=builder /usr/src/config /usr/app/config
COPY --from=builder /usr/src/target/release/db_service-cli /usr/app/db_service-cli

ENTRYPOINT ["/usr/app/db_service-cli", "start", "-e", "production"]
