import os
import pulumi
import pulumi_oci as oci
from pathlib import Path


class oke:
    def create_cluster(self,config,vcn,apiendpoint_subnet,lb_subnet):
        try:
            oke_cluster = oci.containerengine.Cluster("oke_cluster",
                                                        compartment_id=config.get('compartment_ocid'),
                                                        endpoint_config=oci.containerengine.ClusterEndpointConfigArgs(
                                                            is_public_ip_enabled=config.get('oke_is_public_ip_enabled'),
                                                            subnet_id=apiendpoint_subnet.id,
                                                        ),
                                                        name=config.get('oke_cluster_name'),
                                                       kubernetes_version=config.get('kubernetes_version'),
                                                        options=oci.containerengine.ClusterOptionsArgs(
                                                            kubernetes_network_config=oci.containerengine.ClusterOptionsKubernetesNetworkConfigArgs(
                                                                pods_cidr="10.244.0.0/16",
                                                                services_cidr="10.96.0.0/16",
                                                            ),
                                                            persistent_volume_config=oci.containerengine.ClusterOptionsPersistentVolumeConfigArgs(

                                                            ),
                                                            service_lb_config=oci.containerengine.ClusterOptionsServiceLbConfigArgs(

                                                            ),
                                                            service_lb_subnet_ids=[lb_subnet.id],
                                                        ),vcn_id=vcn.id,)
            return  oke_cluster

        except Exception as error:
            print("OKE Cluster creation failed " + str(error))


    def create_nodepool(self,config,oke_cluster,node_subnet):
        try:
            get_ad_name = oci.identity.get_availability_domain(compartment_id=os.environ['TF_VAR_tenancy_ocid'],ad_number=1)
            node_image = oci.core.get_images(compartment_id=config.get('compartment_ocid'),
                                              operating_system=config.get('oke_node_operating_system'),
                                              operating_system_version=config.get('oke_operating_system_version'),
                                              shape=config.get('oke_node_shape'),
                                              sort_by="TIMECREATED",
                                              sort_order="DESC")

            oke_node_pool_1 = oci.containerengine.NodePool("oke_node_pool_1",
                                                            cluster_id=oke_cluster.id,
                                                            compartment_id=config.get('compartment_ocid'),
                                                            initial_node_labels=[oci.containerengine.NodePoolInitialNodeLabelArgs(
                                                                key="name",
                                                                value="pool1",
                                                            )],
                                                            kubernetes_version=config.get('kubernetes_version'),
                                                            name=config.get('oke_nodepool_name'),
                                                            node_config_details=oci.containerengine.NodePoolNodeConfigDetailsArgs(
                                                                placement_configs=[oci.containerengine.NodePoolNodeConfigDetailsPlacementConfigArgs(
                                                                    availability_domain=get_ad_name.__dict__['name'],
                                                                    subnet_id=node_subnet.id,
                                                                )],
                                                                size=int(config.get('oke_nodepool_node_count')),
                                                            ),
                                                            node_shape=config.get('oke_node_shape'),
                                                            node_shape_config=oci.containerengine.NodePoolNodeShapeConfigArgs(
                                                                memory_in_gbs=config.get('oke_node_memory_in_gbs'),
                                                                ocpus=config.get('oke_node_ocpus'),
                                                            ),
                                                            node_source_details=oci.containerengine.NodePoolNodeSourceDetailsArgs(
                                                                image_id=node_image.__dict__['images'][0].get('id'),
                                                                source_type="IMAGE",
                                                            ),

            )
            return oke_node_pool_1
        except Exception as error:
            print("Node pool creation failed " + str(error))

    def create_kubeconfig(self,oke_cluster):
        try:
            cluster_kube_config = oci.containerengine.get_cluster_kube_config(cluster_id=oke_cluster.id)
            Path("generated").mkdir( exist_ok=True)
            file = open('generated/kubeconfig','w+')
            file.write(cluster_kube_config.content)
            file.close()
            return cluster_kube_config
        except Exception as error:
            print("Kubeconfig export is failed" + str(error))


