from pathlib import Path
from resources.output import outputs
from resources.artifact import  artifacts
from resources.devops import devops
from resources.notification import notification
from resources.oke import oke
from resources.random import random_string
from resources.policies import policies
from resources.network import network
from resources.logs import logs
from pulumi import Config



config = Config()
Path('.random.txt').touch(exist_ok=True)

random_string_object = random_string()
random_string_object.create_random_string()
random_string_value=random_string_object.fetch_random_string()

notification_object = notification()
notification_topic = notification_object.create_notification_topic(config)

log_object = logs()
log_group = log_object.create_log_group(config)

policies_object = policies()
pulumi_devopsdg = policies_object.create_dgs(config,random_string_value)
pulumi_devops_policies = policies_object.create_policies(config,random_string_value)


network_object = network()
vcn = network_object.create_vcn(config)
service_gateway = network_object.create_service_gateway(config,vcn)
nat_gateway = network_object.create_natgateway(config,vcn)
internet_gateway = network_object.create_internet_gateway(config,vcn)
node_security_list = network_object.create_node_securitylist(config,vcn)
svclb_security_list = network_object.create_svclb_securitylist(config,vcn)
apiendpoint_security_list = network_object.create_apiendpoint_securitylist(config,vcn)
oke_node_route_table=network_object.create_node_routetable(config,vcn,service_gateway,nat_gateway)
oke_svclb_route_table=network_object.create_svclb_routetable(config,vcn,internet_gateway)
node_subnet = network_object.create_node_subnet(config,vcn,oke_node_route_table,node_security_list)
lb_subnet = network_object.create_lb_subnet(config,vcn,oke_svclb_route_table,svclb_security_list)
apiendpoint_subnet = network_object.create_apiendpoint_subnet(config,vcn,oke_svclb_route_table,apiendpoint_security_list)

artifacts_object=artifacts()
container_repository = artifacts_object.container_repo(config)


oke_object = oke()
oke_cluster = oke_object.create_cluster(config,vcn,apiendpoint_subnet,lb_subnet)
oke_nodepool = oke_object.create_nodepool(config,oke_cluster,node_subnet)
oke_kubeconfig = oke_object.create_kubeconfig(oke_cluster)

devops_object = devops()
devops_project = devops_object.create_devops_project(notification_topic)
artifact_containerrepo,oci_image_uri,namespace = devops_object.create_container_devops_artifact(config,devops_project)
artifact_kubernetes = devops_object.create_kubernetes_devops_artifact(config,devops_project,oci_image_uri)
devops_coderepo = devops_object.create_devops_coderepo(devops_project)
devops_coderepo.http_url.apply(lambda url : devops_object.clone_and_push_code(url))
log = log_object.create_logs(config,log_group,devops_project)
deploy_oke_env = devops_object.create_deploy_env(devops_project,oke_cluster)
devops_build_pipeline = devops_object.create_build_pipeline(config,devops_project)
devops_deploy_pipeline = devops_object.create_deploy_pipeline(config,devops_project)
build_stage_appbuild = devops_object.create_buildstage(config,devops_coderepo,devops_build_pipeline,namespace)
uploadartifact_stage = devops_object.create_uploadartifact_stage(config,devops_build_pipeline,build_stage_appbuild,artifact_containerrepo)
trigerdeployment_stage = devops_object.create_triggerdeploy_stage(config,uploadartifact_stage,devops_build_pipeline,devops_deploy_pipeline)
devployment_stage_to_oke = devops_object.create_deployment_stage(config,devops_deploy_pipeline,artifact_kubernetes,deploy_oke_env)
create_buildrun =devops_object.create_buildrun(config,devops_build_pipeline)

outputs(config)

