import os
import shutil
from git import Repo
import pulumi_oci as oci
from pulumi import Config
from urllib.parse import quote
from resources.random import random_string



class devops:
    def __init__(self):
        self.config = Config()
        self.random_string = random_string().fetch_random_string()

    def create_devops_project(self,notification_topic):

        try:
            devops_project = oci.devops.Project("devops_project",
                                                compartment_id=self.config.get('compartment_ocid'),
                                                name=f"{self.config.get('oci_devops_project_name')}_{self.random_string}",
                                                notification_config=oci.devops.ProjectNotificationConfigArgs(
                                                    topic_id=notification_topic.id,
                                                ),)
            return  devops_project
        except Exception as error:
            print("Devops project creation failed " + str(error))

    def create_devops_coderepo(self,devops_project):
        try:
            devops_coderepo = oci.devops.Repository("devops_coderepo",
                                                     default_branch="refs/heads/main",
                                                     description=self.config.get('devops_coderepo_description'),
                                                     name=self.config.get('devops_coderepo_name'),
                                                     project_id=devops_project.id,
                                                     repository_type="HOSTED")
            return devops_coderepo

        except Exception as error:
            print("Devops coderepo creation failed " + str(error))


    def clone_and_push_code(self,url):
        try:
            git_ocir_username = quote(os.environ['TF_VAR_oci_user'],safe='')
            oci_remote_url = f"https://{git_ocir_username}:{os.environ['TF_VAR_oci_user_password']}@{url.replace('https://','')}"
            if not os.path.exists(self.config.get('github_clone_path')):
                Repo.clone_from(self.config.get('github_url'), self.config.get('github_clone_path'))
            if not os.path.exists(f"{self.config.get('devops_coderepo_name')}_local"):
                Repo.clone_from(oci_remote_url,f"{self.config.get('devops_coderepo_name')}_local")
            shutil.copytree(self.config.get('github_clone_path'), f"{self.config.get('devops_coderepo_name')}_local",dirs_exist_ok=True ,ignore=shutil.ignore_patterns('.git'))
            repo = Repo(f"{self.config.get('devops_coderepo_name')}_local")
            remote = repo.remote(name='origin')
            repo.git.add(all=True)
            repo.index.commit(f"Pushing via remote - Origin ")
            remote.push(refspec='{}:{}'.format('main', 'main'))
        except Exception as error:
            print("Clone and Push code failed " + str(error))

    def create_deploy_env(self,devops_project,oke_cluster):
        try:
            deploy_oke_env = oci.devops.DeployEnvironment("deploy_oke_env",
                                                           cluster_id=oke_cluster.id,
                                                           deploy_environment_type=self.config.get('oci_devops_deploy_env_type'),
                                                           display_name=self.config.get('oci_devops_deploy_env_name'),
                                                           project_id=devops_project.id,
                                                           )
            return deploy_oke_env

        except Exception as error:
            print("Deploy env creation is failing " + str(error))

    def create_container_devops_artifact(self,config,devops_project):
        try:
            namespace = oci.objectstorage.get_namespace(compartment_id=config.get('compartment_ocid'))
            oci_image_uri=f"{os.environ['TF_VAR_region']}.ocir.io/{namespace.namespace}/{config.get('app_name_prefix')}_{config.get('oci_containerrepo_displayname')}:" + "${BUILDRUN_HASH}"
            artifact_containerrepo = oci.devops.DeployArtifact("artifact_containerrepo",
                                                                argument_substitution_mode=config.require('containerartifact_argumentsubstitutionmode'),
                                                                deploy_artifact_source=oci.devops.DeployArtifactDeployArtifactSourceArgs(
                                                                    deploy_artifact_source_type=config.require('containerartifact_sourcetype'),
                                                                    image_uri=oci_image_uri,
                                                                ),
                                                                deploy_artifact_type=config.require('containerartifact_artifacttype'),
                                                                display_name=config.require('containerartifact_displayname'),
                                                                project_id=devops_project.id)
            return  artifact_containerrepo,oci_image_uri,namespace


        except Exception as error:
            print("Devops  container erpo artifact creation failed" + str(error))

    def create_kubernetes_devops_artifact(self,config,devops_project,oci_image_uri):
        try:
            with open('manifest/kubernetes-deploymentspec.yaml','r') as stream:
                filedata = stream.read()
            filedata=filedata.replace('oci_image_url',oci_image_uri)

            artifact_kubernetes = oci.devops.DeployArtifact("artifact_kubernetes",
                                                             argument_substitution_mode="SUBSTITUTE_PLACEHOLDERS",
                                                             deploy_artifact_source=oci.devops.DeployArtifactDeployArtifactSourceArgs(
                                                                 base64encoded_content=filedata,
                                                                 deploy_artifact_source_type=config.require('deploy_artifact_source_type'),
                                                             ),
                                                             deploy_artifact_type=config.require('kuberartifact_sourcetype'),
                                                             display_name=config.require('kuberartifact_displayname'),
                                                             project_id=devops_project.id)

            return artifact_kubernetes


        except Exception as error:
            print("Kubernetes artifact creation failed " + str(error))


    def create_build_pipeline(self,config,devops_project):
        try:
            devops_build_pipeline = oci.devops.BuildPipeline("devops_build_pipeline",
                                                              build_pipeline_parameters=oci.devops.BuildPipelineBuildPipelineParametersArgs(
                                                                  items=[oci.devops.BuildPipelineBuildPipelineParametersItemArgs(
                                                                      name="BUILDRUN_HASH",
                                                                      default_value="NA",
                                                                      description="Tag for container image"
                                                                  )]
                                                              ),
                                                              description=config.require('devop_buildpipeline_description'),
                                                              display_name=config.require('devop_buildpipeline_name'),
                                                              project_id=devops_project.id)
            return  devops_build_pipeline
        except Exception as error:
            print ("Buildpipeline creation failed" + str(error))

    def create_deploy_pipeline(self,config,devops_project):
        try:
            ocidevops_pipeline = oci.devops.DeployPipeline("ocidevops_pipeline",
                                                            deploy_pipeline_parameters=oci.devops.DeployPipelineDeployPipelineParametersArgs(
                                                                items=[oci.devops.DeployPipelineDeployPipelineParametersItemArgs(
                                                                    default_value=config.require('deploypipeline_param_defaultvalue'),
                                                                    description=config.require('deploypipeline_param_description'),
                                                                    name=config.require('deploypipeline_param_name'),
                                                                )],
                                                            ),
                                                            description=config.require('deploypipeline_description'),
                                                            display_name=config.require('deploypipeline_displayname'),
                                                            project_id=devops_project.id)
            return  ocidevops_pipeline

        except Exception as error:
            print ("Deploypipeline creation failed" + str(error))

    def create_buildstage(self,config,devops_coderepo,devops_build_pipeline,namespace):
        try:
            repository_url = f"https://devops.scmservice.{os.environ['TF_VAR_region']}.oci.oraclecloud.com/namespaces/" + \
                             f"{namespace.namespace}/projects/{config.get('oci_devops_project_name')}_{self.random_string}/repositories/{config.get('devops_coderepo_name')}"
            build_stage_appbuild = oci.devops.BuildPipelineStage("build_stage_appbuild",
                                                                  build_pipeline_id=devops_build_pipeline.id,
                                                                  build_pipeline_stage_predecessor_collection=oci.devops.BuildPipelineStageBuildPipelineStagePredecessorCollectionArgs(
                                                                      items=[oci.devops.BuildPipelineStageBuildPipelineStagePredecessorCollectionItemArgs(
                                                                          id=devops_build_pipeline.id,
                                                                      )],
                                                                  ),
                                                                  build_pipeline_stage_type=config.require('buildstage_stagetype'),
                                                                  build_source_collection=oci.devops.BuildPipelineStageBuildSourceCollectionArgs(
                                                                      items=[oci.devops.BuildPipelineStageBuildSourceCollectionItemArgs(
                                                                          branch=config.require('buildstage_branchname'),
                                                                          connection_type=config.require('buildstage_connection_type'),
                                                                          name=config.require('buildstage_sourcename'),
                                                                          repository_id=devops_coderepo.id,
                                                                          repository_url=repository_url
                                                                     )],
                                                                  ),
                                                                  build_spec_file=config.require('build_spec_file'),
                                                                  description=config.require('buildstage_description'),
                                                                  display_name=config.require('buildstage_displayname'),
                                                                  image=config.require('buildstage_image'),
                                                                  primary_build_source=config.require('buildstage_sourcename'),
                                                                  )
            return  build_stage_appbuild
        except Exception as error:
            print("Build stage creation failed" + str(error))

    def create_uploadartifact_stage(self,config,devops_build_pipeline,build_stage_appbuild,artifact_containerrepo):
        try:
            uploadartifact_stage = oci.devops.BuildPipelineStage("uploadartifact_stage",
                                                                  build_pipeline_id=devops_build_pipeline.id,
                                                                  build_pipeline_stage_predecessor_collection=oci.devops.BuildPipelineStageBuildPipelineStagePredecessorCollectionArgs(
                                                                      items=[oci.devops.BuildPipelineStageBuildPipelineStagePredecessorCollectionItemArgs(
                                                                          id=build_stage_appbuild.id,
                                                                      )],
                                                                  ),
                                                                  build_pipeline_stage_type=config.require('uploadartifact_stagetype'),
                                                                  deliver_artifact_collection=oci.devops.BuildPipelineStageDeliverArtifactCollectionArgs(
                                                                      items=[oci.devops.BuildPipelineStageDeliverArtifactCollectionItemArgs(
                                                                          artifact_id=artifact_containerrepo.id,
                                                                          artifact_name=config.require('uploadartifact_source'),
                                                                      )],
                                                                  ),
                                                                  description=config.require('uploadartifact_description'),
                                                                  display_name=config.require('uploadartifact_displayname'))
            return  uploadartifact_stage


        except Exception as error:
            print("Uploadartifact stage creation failed" + str(error))

    def create_triggerdeploy_stage(self,config,uploadartifact_stage,devops_build_pipeline,devops_deploy_pipeline):
        try:
            trigerdeployment_stage = oci.devops.BuildPipelineStage("trigerdeployment_stage",
                                                                    build_pipeline_id=devops_build_pipeline.id,
                                                                    build_pipeline_stage_predecessor_collection=oci.devops.BuildPipelineStageBuildPipelineStagePredecessorCollectionArgs(
                                                                        items=[oci.devops.BuildPipelineStageBuildPipelineStagePredecessorCollectionItemArgs(
                                                                            id=uploadartifact_stage.id,
                                                                        )],
                                                                    ),
                                                                    build_pipeline_stage_type=config.require('trigerdeployment_stagetype'),
                                                                    deploy_pipeline_id=devops_deploy_pipeline.id,
                                                                    description=config.require('trigerdeployment_description'),
                                                                    display_name=config.require('trigerdeployment_name'),
                                                                    is_pass_all_parameters_enabled=config.require('trigerdeployment_parseparamenabled'))
            return  trigerdeployment_stage

        except Exception as error:
            print("Trigerdeploy stage creation failed" + str(error))

    def create_deployment_stage(self,config,devops_deploy_pipeline,artifact_kubernetes,deploy_oke_env):
        try:
            deployto_oke = oci.devops.DeployStage("deployto_oke",
                                                   deploy_pipeline_id=devops_deploy_pipeline.id,
                                                   deploy_stage_predecessor_collection=oci.devops.DeployStageDeployStagePredecessorCollectionArgs(
                                                       items=[oci.devops.DeployStageDeployStagePredecessorCollectionItemArgs(
                                                           id=devops_deploy_pipeline.id,
                                                       )],
                                                   ),
                                                   deploy_stage_type=config.require('deploystage_oke_type'),
                                                   description=config.require('deploystage_oke_description'),
                                                   display_name=config.require('deploystage_oke_name'),
                                                   kubernetes_manifest_deploy_artifact_ids=[artifact_kubernetes.id],
                                                   oke_cluster_deploy_environment_id=deploy_oke_env.id,
                                                   rollback_policy=oci.devops.DeployStageRollbackPolicyArgs(
                                                       policy_type=config.require('deploystage_oke_rollbackpolicy'),
                                                   ))
            return deployto_oke

        except Exception as error:
            print("Deployment stage creation failed" + str(error))

    def create_buildrun(self,config,devops_build_pipeline):
        try:
            if (config.require('autobuild_run') == "True"):
                auto_buildrun = oci.devops.BuildRun("auto_buildrun",opts=ResourceOptions(depends_on=["deployto_oke","oke_node_pool_1"],
                                                     build_pipeline_id=devops_build_pipeline.id,
                                                     build_run_arguments=oci.devops.BuildRunBuildRunArgumentsArgs(
                                                         items=[oci.devops.BuildRunBuildRunArgumentsItemArgs(
                                                             name="BUILDRUN_HASH",
                                                             value="NA",
                                                         )],
                                                     ),

                                                     display_name=f"buildrun-ocidevops-with-pulumi-{self.random_string}")
                return  auto_buildrun

            else:
                print("Auto build run is not enabled,enabled it - pulumi config set autobuild_run True  and pulumi up. ")
        except Exception as error:
            print("Auto buildrun failed" + str(error))