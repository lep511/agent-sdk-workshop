FROM public.ecr.aws/lambda/python:3.13-arm64

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY lib/ ${LAMBDA_TASK_ROOT}/lib/
COPY examples/ ${LAMBDA_TASK_ROOT}/examples/

# Make example directories proper packages for dotted import paths
RUN touch ${LAMBDA_TASK_ROOT}/examples/__init__.py \
    && touch ${LAMBDA_TASK_ROOT}/examples/01_basic_durable_agent/__init__.py \
    && touch ${LAMBDA_TASK_ROOT}/examples/02_human_approval_agent/__init__.py \
    && touch ${LAMBDA_TASK_ROOT}/examples/03_multi_agent_orchestrator/__init__.py

ENV CLAUDE_CODE_USE_BEDROCK=1
ENV CLAUDE_CONFIG_DIR=/tmp

CMD ["examples.01_basic_durable_agent.handler.handler"]
