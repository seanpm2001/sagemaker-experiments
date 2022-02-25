# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
"""Contains the TrialComponent class."""
from smexperiments import _base_types, api_types, trial
import time


class TrialComponent(_base_types.Record):
    """This class represents a SageMaker trial component object.

    A trial component is a stage in a trial.

    Trial components are created automatically within the SageMaker runtime and may not be created directly.
    To automatically associate trial components with a trial and experiment supply an experiment config when creating a
    job. For example: https://docs.aws.amazon.com/sagemaker/latest/dg/API_CreateTrainingJob.html

    Parameters:
        trial_component_name (str): The name of the trial component. Generated by SageMaker from the name of the
            source job with a suffix specific to the type of source job.
        trial_component_arn (str): The ARN of the trial component.
        display_name (str): The name of the trial component that will appear in UI, such as SageMaker Studio.
        source (obj): A TrialComponentSource object with a source_arn attribute.
        status (str): Status of the source job.
        start_time (datetime): When the source job started.
        end_time (datetime): When the source job ended.
        creation_time (datetime): When the source job was created.
        created_by (obj): Contextual info on which account created the trial component.
        last_modified_time (datetime): When the trial component was last modified.
        last_modified_by (obj): Contextual info on which account last modified the trial component.
        parameters (dict): Dictionary of parameters to the source job.
        input_artifacts (dict): Dictionary of input artifacts.
        output_artifacts (dict): Dictionary of output artifacts.
        metrics (obj): Aggregated metrics for the job.
        parameters_to_remove (list): The hyperparameters to remove from the component.
        input_artifacts_to_remove (list): The input artifacts to remove from the component.
        output_artifacts_to_remove (list): The output artifacts to remove from the component.
        tags (List[dict[str, str]]): A list of tags to associate with the trial component.
    """

    trial_component_name = None
    trial_component_arn = None
    display_name = None
    source = None
    status = None
    start_time = None
    end_time = None
    creation_time = None
    created_by = None
    last_modified_time = None
    last_modified_by = None
    parameters = None
    input_artifacts = None
    output_artifacts = None
    metrics = None
    parameters_to_remove = None
    input_artifacts_to_remove = None
    output_artifacts_to_remove = None
    tags = None

    _boto_load_method = "describe_trial_component"
    _boto_create_method = "create_trial_component"
    _boto_update_method = "update_trial_component"
    _boto_delete_method = "delete_trial_component"

    _custom_boto_types = {
        "source": (api_types.TrialComponentSource, False),
        "status": (api_types.TrialComponentStatus, False),
        "parameters": (api_types.TrialComponentParameters, False),
        "input_artifacts": (api_types.TrialComponentArtifact, True),
        "output_artifacts": (api_types.TrialComponentArtifact, True),
        "metrics": (api_types.TrialComponentMetricSummary, True),
    }

    _boto_update_members = [
        "trial_component_name",
        "display_name",
        "status",
        "start_time",
        "end_time",
        "parameters",
        "input_artifacts",
        "output_artifacts",
        "parameters_to_remove",
        "input_artifacts_to_remove",
        "output_artifacts_to_remove",
    ]
    _boto_delete_members = ["trial_component_name"]

    @classmethod
    def _boto_ignore(cls):
        return super(TrialComponent, cls)._boto_ignore() + ["CreatedBy"]

    def save(self):
        """Save the state of this TrialComponent to SageMaker."""
        return self._invoke_api(self._boto_update_method, self._boto_update_members)

    def delete(self, force_disassociate=None):
        """Delete this TrialComponent from SageMaker.

        Args:
            force_disassociate (boolean): Indicates whether to force disassociate the trial component with the trials
            before deletion. If set to true, force disassociate the trial component with associated trials first, then
            delete the trial component. If it's not set or set to false, it will delete the trial component directory
             without disassociation.

          Returns:
            dict: Delete trial component response.
        """
        if force_disassociate:
            next_token = None

            while True:
                if next_token:
                    list_trials_response = self.sagemaker_boto_client.list_trials(
                        TrialComponentName=self.trial_component_name, NextToken=next_token
                    )
                else:
                    list_trials_response = self.sagemaker_boto_client.list_trials(
                        TrialComponentName=self.trial_component_name
                    )

                # Disassociate the trials and trial components
                for per_trial in list_trials_response["TrialSummaries"]:
                    # to prevent DisassociateTrialComponent throttling
                    time.sleep(1.2)
                    self.sagemaker_boto_client.disassociate_trial_component(
                        TrialName=per_trial["TrialName"], TrialComponentName=self.trial_component_name
                    )

                if "NextToken" in list_trials_response:
                    next_token = list_trials_response["NextToken"]
                else:
                    break

        return self._invoke_api(self._boto_delete_method, self._boto_delete_members)

    def list_trials(self):
        """
        Load a list of trials that contains the same trial component name

        Returns:
            A list of trials that contains the same trial component name
        """
        return trial.Trial.list(
            trial_component_name=self.trial_component_name, sagemaker_boto_client=self.sagemaker_boto_client
        )

    @classmethod
    def load(cls, trial_component_name, sagemaker_boto_client=None):
        """Load an existing trial component and return an ``TrialComponent`` object representing it.

        Args:
            trial_component_name (str): Name of the trial component
            sagemaker_boto_client (SageMaker.Client, optional): Boto3 client for SageMaker.
                If not supplied, a default boto3 client will be created and used.

        Returns:
            smexperiments.trial_component.TrialComponent: A SageMaker ``TrialComponent`` object
        """
        trial_component = cls._construct(
            cls._boto_load_method,
            trial_component_name=trial_component_name,
            sagemaker_boto_client=sagemaker_boto_client,
        )
        return trial_component

    @classmethod
    def create(cls, trial_component_name, display_name=None, tags=None, sagemaker_boto_client=None):
        """Create a trial component and return a ``TrialComponent`` object representing it.

        Args:
            trial_component_name (str): The name of the trial component.
            display_name (str): Display name of the trial component used by Studio. Defaults to
                None.
            tags (dict): Tags to add to the trial component. Defaults to None.
            sagemaker_boto_client (obj): SageMaker boto client. Defaults to None.

        Returns:
            smexperiments.trial_component.TrialComponent: A SageMaker ``TrialComponent``
                object.
        """
        return super(TrialComponent, cls)._construct(
            cls._boto_create_method,
            trial_component_name=trial_component_name,
            display_name=display_name,
            tags=tags,
            sagemaker_boto_client=sagemaker_boto_client,
        )

    @classmethod
    def list(
        cls,
        source_arn=None,
        created_before=None,
        created_after=None,
        sort_by=None,
        sort_order=None,
        sagemaker_boto_client=None,
        trial_name=None,
        experiment_name=None,
        max_results=None,
        next_token=None,
    ):
        """Return a list of trial component summaries.

        Args:
            source_arn (str, optional): A SageMaker Training or Processing Job ARN.
            created_before (datetime.datetime, optional): Return trial components created before this instant.
            created_after (datetime.datetime, optional): Return trial components created after this instant.
            sort_by (str, optional): Which property to sort results by. One of 'SourceArn', 'CreatedBefore',
                'CreatedAfter'
            sort_order (str, optional): One of 'Ascending', or 'Descending'.
            sagemaker_boto_client (SageMaker.Client, optional) : Boto3 client for SageMaker.
                If not supplied, a default boto3 client will be created and used.
            trial_name (str, optional): If provided only trial components related to the trial are returned.
            experiment_name (str, optional): If provided only trial components related to the experiment are returned.
            max_results (int, optional): maximum number of trial components to retrieve
            next_token (str, optional): token for next page of results

        Returns:
            collections.Iterator[smexperiments.api_types.TrialComponentSummary]: An iterator
                over ``TrialComponentSummary`` objects.
        """
        return super(TrialComponent, cls)._list(
            "list_trial_components",
            api_types.TrialComponentSummary.from_boto,
            "TrialComponentSummaries",
            source_arn=source_arn,
            created_before=created_before,
            created_after=created_after,
            sort_by=sort_by,
            sort_order=sort_order,
            sagemaker_boto_client=sagemaker_boto_client,
            trial_name=trial_name,
            experiment_name=experiment_name,
            max_results=max_results,
            next_token=next_token,
        )

    @classmethod
    def search(
        cls,
        search_expression=None,
        sort_by=None,
        sort_order=None,
        max_results=None,
        sagemaker_boto_client=None,
    ):
        """
        Search experiments. Returns SearchResults in the account matching the search criteria.

        Args:
            search_expression: (dict, optional): A Boolean conditional statement. Resource objects
                must satisfy this condition to be included in search results. You must provide at
                least one subexpression, filter, or nested filter.
            sort_by (str, optional): The name of the resource property used to sort the SearchResults.
                The default is LastModifiedTime
            sort_order (str, optional): How SearchResults are ordered. Valid values are Ascending or
                Descending . The default is Descending .
            max_results (int, optional): The maximum number of results to return in a SearchResponse.
            sagemaker_boto_client (SageMaker.Client, optional): Boto3 client for SageMaker. If not
                supplied, a default boto3 client will be used.

        Returns:
            collections.Iterator[SearchResult] : An iterator over search results matching the
            search criteria.
        """
        return super(TrialComponent, cls)._search(
            search_resource="ExperimentTrialComponent",
            search_item_factory=api_types.TrialComponentSearchResult.from_boto,
            search_expression=None if search_expression is None else search_expression.to_boto(),
            sort_by=sort_by,
            sort_order=sort_order,
            max_results=max_results,
            sagemaker_boto_client=sagemaker_boto_client,
        )
