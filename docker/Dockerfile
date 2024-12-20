FROM apache/airflow:2.10.3

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

USER root

# Install Java (OpenJDK 17)
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget gnupg ca-certificates && \
    wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptium-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/adoptium-archive-keyring.gpg] https://packages.adoptium.net/artifactory/deb/ $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/adoptium.list && \
    apt-get update && \
    apt-get install -y temurin-17-jre procps && \
    apt-get autoremove -yqq --purge && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME to Java 17 path
ENV JAVA_HOME=/usr/lib/jvm/temurin-17-jre-arm64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install necessary Spark and Hadoop dependencies
RUN mkdir -p /opt/spark/jars

# Install Apache Hadoop
ARG HADOOP_VERSION=2.10.1
ENV HADOOP_HOME=/opt/hadoop
ENV HADOOP_CONF_DIR=/etc/hadoop
ENV MULTIHOMED_NETWORK=1

RUN HADOOP_URL="https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz" \
    && curl 'https://dist.apache.org/repos/dist/release/hadoop/common/KEYS' | gpg --import - \
    && curl -fSL "$HADOOP_URL" -o /tmp/hadoop.tar.gz \
    && curl -fSL "$HADOOP_URL.asc" -o /tmp/hadoop.tar.gz.asc \
    && gpg --verify /tmp/hadoop.tar.gz.asc \
    && mkdir -p "${HADOOP_HOME}" \
    && tar -xvf /tmp/hadoop.tar.gz -C "${HADOOP_HOME}" --strip-components=1 \
    && rm /tmp/hadoop.tar.gz /tmp/hadoop.tar.gz.asc \
    && ln -s "${HADOOP_HOME}/etc/hadoop" /etc/hadoop \
    && mkdir "${HADOOP_HOME}/logs" \
    && mkdir /hadoop-data

ENV PATH="$HADOOP_HOME/bin:$PATH"

# Install Apache Hive
ARG HIVE_VERSION=2.3.7
ENV HIVE_HOME=/opt/hive
ENV HIVE_CONF_DIR=/etc/hive

RUN HIVE_URL="https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz" \
    && curl -fSL 'https://downloads.apache.org/hive/KEYS' | gpg --import - \
    && curl -fSL "$HIVE_URL" -o /tmp/hive.tar.gz \
    && curl -fSL "$HIVE_URL.asc" -o /tmp/hive.tar.gz.asc \
    && gpg --verify /tmp/hive.tar.gz.asc \
    && mkdir -p "${HIVE_HOME}" \
    && tar -xf /tmp/hive.tar.gz -C "${HIVE_HOME}" --strip-components=1 \
    && rm /tmp/hive.tar.gz /tmp/hive.tar.gz.asc \
    && ln -s "${HIVE_HOME}/etc/hive" "${HIVE_CONF_DIR}" \
    && mkdir "${HIVE_HOME}/logs"

ENV PATH="$HIVE_HOME/bin:$PATH"

# Install GCS connector for Apache Hadoop
ARG GCS_VARIANT="hadoop2"
ARG GCS_VERSION="2.1.5"

RUN GCS_JAR_PATH="/opt/spark/jars/gcs-connector-${GCS_VARIANT}-${GCS_VERSION}.jar" \
    && GCS_JAR_URL="https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-${GCS_VARIANT}-${GCS_VERSION}.jar" \
    && curl "${GCS_JAR_URL}" -o "${GCS_JAR_PATH}"

ENV HADOOP_CLASSPATH="/opt/spark/jars/gcs-connector-${GCS_VARIANT}-${GCS_VERSION}.jar:$HADOOP_CLASSPATH"

USER airflow

# Install Airflow and Spark dependencies
RUN pip install apache-airflow-providers-mysql apache-airflow-providers-apache-spark pyspark pymysql

