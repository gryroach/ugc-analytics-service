FROM bitnami/kafka:3.4

# Add health check script
COPY ./healthcheck.sh /healthcheck.sh

# Define health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 CMD /healthcheck.sh
