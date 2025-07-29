import pandas as pd

import vertexai
from vertexai.evaluation import EvalTask, PointwiseMetric, PointwiseMetricPromptTemplate
from google.cloud import aiplatform
from agent import root_agent

PROJECT_ID = "gossy-workstations"
LOCATION = "us-central1"
EXPERIMENT_NAME = "experiment-name"

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
)

# Define a pointwise metric with two criteria: Fluency and Entertaining.
custom_text_quality = PointwiseMetric(
    metric="custom_text_quality",
    metric_prompt_template=PointwiseMetricPromptTemplate(
        criteria={
            "fluency": (
                "Sentences flow smoothly and are easy to read, avoiding awkward"
                " phrasing or run-on sentences. Ideas and sentences connect"
                " logically, using transitions effectively where needed."
            ),
            "entertaining": (
                "Short, amusing text that incorporates emojis, exclamations and"
                " questions to convey quick and spontaneous communication and"
                " diversion."
            ),
        },
        rating_rubric={
            "1": "The response performs well on both criteria.",
            "0": "The response is somewhat aligned with both criteria",
            "-1": "The response falls short on both criteria",
        },
    ),
)

responses = [
    # An example of good custom_text_quality
    "Life is a rollercoaster, full of ups and downs, but it's the thrill that keeps us coming back for more!",
    # An example of medium custom_text_quality
    "The weather is nice today, not too hot, not too cold.",
    # An example of poor custom_text_quality
    "The weather is, you know, whatever.",
]

eval_dataset = pd.DataFrame({
    "response" : responses,
})

eval_task = EvalTask(
    dataset=eval_dataset,
    metrics=[custom_text_quality],
    experiment=EXPERIMENT_NAME
)

pointwise_result = eval_task.evaluate()
print(pointwise_result)