import pulumi_oci as oci

class network:
    def create_vcn(self,config):
        try:
            test_vcn = oci.core.Vcn("vcn",
                                    cidr_blocks=[config.get('vcn_cidr_block')],
                                    compartment_id=config.get('compartment_ocid'),
                                    display_name=config.get('vcn_display_name'),
                                    dns_label=config.get('vcn_dns_label'),
                                    )
            return  test_vcn


        except Exception as error:
            print("VNC Creation failed " + str(error))

    def create_natgateway(self,config,vcn):
        try:
            nat_gateway = oci.core.NatGateway("nat_gateway",
                                                   compartment_id=config.get('compartment_ocid'),
                                                   display_name=config.get('natgateway_name'),
                                                   vcn_id=vcn.id,)

            return  nat_gateway
        except Exception as error:
            print("Nat gateway Creation failed " + str(error))

    def create_internet_gateway(self,config,vcn):
        try:
            oke_internet_gateway = oci.core.InternetGateway("oke_internet_gateway",
                                                            compartment_id=config.get('compartment_ocid'),
                                                            display_name=config.get('internetgateway_name'),
                                                            vcn_id=vcn.id)
            return  oke_internet_gateway

        except Exception as error:
            print("Internet gateway Creation failed " + str(error))



    def create_service_gateway(self,config,vcn):
        try:

            service_gateway = oci.core.ServiceGateway("service_gateway",
                                                           compartment_id=config.get('compartment_ocid'),
                                                           display_name=config.get('servicegateway_name'),
                                                           services=[oci.core.ServiceGatewayServiceArgs(
                                                               service_id=oci.core.get_services().services[1].id,
                                                           )],
                                                           vcn_id=vcn.id,
                                                           )
            return  service_gateway
        except Exception as error:
            print("Service gateway Creation failed " + str(error))

    def create_svclb_securitylist(self,config,vcn):
        try:
            svclb_security_list = oci.core.SecurityList("svclb_security_list",
                                                        compartment_id=config.get('compartment_ocid'),
                                                        display_name=config.get('oke_svclb_seclist_name'),
                                                        vcn_id=vcn.id)
            return  svclb_security_list


        except Exception as error:
            print("svcLB security list creation failed " + str(error))

    def create_apiendpoint_securitylist(self,config,vcn):
        try:
            apiendpoint_security_list = oci.core.SecurityList("apiendpoint_security_list",
                                                              compartment_id=config.get('compartment_ocid'),
                                                              display_name=config.get('oke_apiendpoint_seclist_name'),
                                                              egress_security_rules=[
                                                                  oci.core.SecurityListEgressSecurityRuleArgs(
                                                                      description="Path discovery",
                                                                      destination="10.0.10.0/24",
                                                                      destination_type="CIDR_BLOCK",
                                                                      icmp_options=oci.core.SecurityListEgressSecurityRuleIcmpOptionsArgs(
                                                                          code=4,
                                                                          type=3,
                                                                      ),
                                                                      protocol="1",
                                                                  ),
                                                                  oci.core.SecurityListEgressSecurityRuleArgs(
                                                                      description="Allow Kubernetes Control Plane to communicate with OKE",
                                                                      destination="all-iad-services-in-oracle-services-network",
                                                                      destination_type="SERVICE_CIDR_BLOCK",
                                                                      protocol="6",
                                                                      tcp_options=oci.core.SecurityListEgressSecurityRuleTcpOptionsArgs(
                                                                          max=443,
                                                                          min=443,
                                                                      ),
                                                                  ),
                                                                  oci.core.SecurityListEgressSecurityRuleArgs(
                                                                      description="All traffic to worker nodes",
                                                                      destination="10.0.10.0/24",
                                                                      destination_type="CIDR_BLOCK",
                                                                      protocol="6",
                                                                  ),
                                                              ],
                                                              ingress_security_rules=[
                                                                  oci.core.SecurityListIngressSecurityRuleArgs(
                                                                      description="Kubernetes worker to control plane communication",
                                                                      protocol="6",
                                                                      source="10.0.10.0/24",
                                                                      source_type="CIDR_BLOCK",
                                                                      tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                                                                          max=12250,
                                                                          min=12250,
                                                                      ),
                                                                  ),
                                                                  oci.core.SecurityListIngressSecurityRuleArgs(
                                                                      description="Kubernetes worker to Kubernetes API endpoint communication",
                                                                      protocol="6",
                                                                      source="10.0.10.0/24",
                                                                      source_type="CIDR_BLOCK",
                                                                      tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                                                                          max=6443,
                                                                          min=6443,
                                                                      ),
                                                                  ),
                                                                  oci.core.SecurityListIngressSecurityRuleArgs(
                                                                      description="External access to Kubernetes API endpoint",
                                                                      protocol="6",
                                                                      source="0.0.0.0/0",
                                                                      source_type="CIDR_BLOCK",
                                                                      tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                                                                          max=6443,
                                                                          min=6443,
                                                                      ),
                                                                  ),
                                                                  oci.core.SecurityListIngressSecurityRuleArgs(
                                                                      description="Path discovery",
                                                                      icmp_options=oci.core.SecurityListIngressSecurityRuleIcmpOptionsArgs(
                                                                          code=4,
                                                                          type=3,
                                                                      ),
                                                                      protocol="1",
                                                                      source="10.0.10.0/24",
                                                                      source_type="CIDR_BLOCK",
                                                                  ),
                                                              ],
                                                              vcn_id=vcn.id)
            return apiendpoint_security_list


        except Exception as error:
            print("apiEndpoint security list creation failed " + str(error))


    def create_node_securitylist(self,config,vcn):
        try:
            node_security_list = oci.core.SecurityList("node_security_list",
                                                       compartment_id=config.get('compartment_ocid'),
                                                       display_name=config.get('oke_node_seclist_name'),
                                                       egress_security_rules=[
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="Kubernetes worker to control plane communication",
                                                               destination="10.0.0.0/28",
                                                               destination_type="CIDR_BLOCK",
                                                               protocol="6",
                                                               tcp_options=oci.core.SecurityListEgressSecurityRuleTcpOptionsArgs(
                                                                   max=12250,
                                                                   min=12250,
                                                               ),
                                                           ),
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="Worker Nodes access to Internet",
                                                               destination="0.0.0.0/0",
                                                               destination_type="CIDR_BLOCK",
                                                               protocol="all",
                                                           ),
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="Access to Kubernetes API Endpoint",
                                                               destination="10.0.0.0/28",
                                                               destination_type="CIDR_BLOCK",
                                                               protocol="6",
                                                               tcp_options=oci.core.SecurityListEgressSecurityRuleTcpOptionsArgs(
                                                                   max=6443,
                                                                   min=6443,
                                                               ),
                                                           ),
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="Path discovery",
                                                               destination="10.0.0.0/28",
                                                               destination_type="CIDR_BLOCK",
                                                               icmp_options=oci.core.SecurityListEgressSecurityRuleIcmpOptionsArgs(
                                                                   code=4,
                                                                   type=3,
                                                               ),
                                                               protocol="1",
                                                           ),
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="ICMP Access from Kubernetes Control Plane",
                                                               destination="0.0.0.0/0",
                                                               destination_type="CIDR_BLOCK",
                                                               icmp_options=oci.core.SecurityListEgressSecurityRuleIcmpOptionsArgs(
                                                                   code=4,
                                                                   type=3,
                                                               ),
                                                               protocol="1",
                                                           ),
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="Allow nodes to communicate with OKE to ensure correct start-up and continued functioning",
                                                               destination=oci.core.get_services().services[1].cidr_block,
                                                               destination_type="SERVICE_CIDR_BLOCK",
                                                               protocol="6",
                                                               tcp_options=oci.core.SecurityListEgressSecurityRuleTcpOptionsArgs(
                                                                   max=443,
                                                                   min=443,
                                                               ),
                                                           ),
                                                           oci.core.SecurityListEgressSecurityRuleArgs(
                                                               description="Allow pods on one worker node to communicate with pods on other worker nodes",
                                                               destination="10.0.10.0/24",
                                                               destination_type="CIDR_BLOCK",
                                                               protocol="all",
                                                           ),
                                                       ],
                                                       ingress_security_rules=[
                                                           oci.core.SecurityListIngressSecurityRuleArgs(
                                                               description="Path discovery",
                                                               icmp_options=oci.core.SecurityListIngressSecurityRuleIcmpOptionsArgs(
                                                                   code=4,
                                                                   type=3,
                                                               ),
                                                               protocol="1",
                                                               source="10.0.0.0/28",
                                                               source_type="CIDR_BLOCK",
                                                           ),
                                                           oci.core.SecurityListIngressSecurityRuleArgs(
                                                               description="Inbound SSH traffic to worker nodes",
                                                               protocol="6",
                                                               source="0.0.0.0/0",
                                                               source_type="CIDR_BLOCK",
                                                               tcp_options=oci.core.SecurityListIngressSecurityRuleTcpOptionsArgs(
                                                                   max=22,
                                                                   min=22,
                                                               ),
                                                           ),
                                                           oci.core.SecurityListIngressSecurityRuleArgs(
                                                               description="Allow pods on one worker node to communicate with pods on other worker nodes",
                                                               protocol="all",
                                                               source="10.0.10.0/24",
                                                               source_type="CIDR_BLOCK",
                                                           ),
                                                           oci.core.SecurityListIngressSecurityRuleArgs(
                                                               description="TCP access from Kubernetes Control Plane",
                                                               protocol="6",
                                                               source="10.0.0.0/28",
                                                               source_type="CIDR_BLOCK",
                                                           ),
                                                       ],
                                                       vcn_id=vcn.id)
            return  node_security_list
        except Exception as error:
            print("Node security list creation failed " + str(error))

    def create_node_routetable(self,config,vcn,service_gateway,nat_gateway):
        try:
            oke_node_route_table = oci.core.RouteTable("oke_node_route_table",
                                                       compartment_id=config.get('compartment_ocid'),
                                                       display_name=config.get('oke_node_routetable_displayname'),
                                                       route_rules=[
                                                           oci.core.RouteTableRouteRuleArgs(
                                                               description="traffic to OCI services",
                                                               destination="all-iad-services-in-oracle-services-network",
                                                               destination_type="SERVICE_CIDR_BLOCK",
                                                               network_entity_id=service_gateway.id,
                                                           ),
                                                           oci.core.RouteTableRouteRuleArgs(
                                                               description="traffic to the internet",
                                                               destination="0.0.0.0/0",
                                                               destination_type="CIDR_BLOCK",
                                                               network_entity_id=nat_gateway.id,
                                                           ),
                                                       ],
                                                       vcn_id=vcn.id)
            return  oke_node_route_table

        except Exception as error:
            print("Node route table creation failed " + str(error))

    def create_svclb_routetable(self,config,vcn,internet_gateway):
        try:
            oke_svclb_route_table = oci.core.RouteTable("oke_svclb_route_table",
                                                        compartment_id=config.get('compartment_ocid'),
                                                        display_name=config.get('oke_svclb_routetable_displayname'),
                                                        route_rules=[oci.core.RouteTableRouteRuleArgs(
                                                            description="traffic to/from internet",
                                                            destination="0.0.0.0/0",
                                                            destination_type="CIDR_BLOCK",
                                                            network_entity_id=internet_gateway.id,
                                                        )],
                                                        vcn_id=vcn.id)
            return  oke_svclb_route_table


        except Exception as error:
            print("SvcLb route table creation failed " + str(error))

    def create_node_subnet(self,config,vcn,oke_node_route_table,node_security_list):
        try:
            node_subnet = oci.core.Subnet("node_subnet",
                                          cidr_block=config.get('oke_nodesubnet_cidr'),
                                          compartment_id=config.get('compartment_ocid'),
                                          # dhcp_options_id="ocid1.dhcpoptions.oc1.iad.aaaaaaaac7urxcbaietlipbfutlszxcgcvi5gqsadxqkmuu2u3mc5jwqzkhq",
                                          display_name=config.get('oke_nodesubnet_displayname'),
                                          # dns_label="subcb2ee1d7f",
                                          # prohibit_internet_ingress=True,
                                          # prohibit_public_ip_on_vnic=True,
                                          route_table_id=oke_node_route_table.id,
                                          security_list_ids=[node_security_list.id],
                                          vcn_id=vcn.id,
                                          )

            return  node_subnet
        except Exception as error:
            print("Node subnet Creation failed " + str(error))

    def create_lb_subnet(self,config,vcn,oke_svclb_route_table,svclb_security_list):
        try:
            lb_subnet = oci.core.Subnet("lb_subnet",
                                        cidr_block=config.get('oke_lbsubnet_cidr'),
                                        compartment_id=config.get('compartment_ocid'),
                                        # dhcp_options_id="ocid1.dhcpoptions.oc1.iad.aaaaaaaac7urxcbaietlipbfutlszxcgcvi5gqsadxqkmuu2u3mc5jwqzkhq",
                                        display_name=config.get('oke_lbsubnet_displayname'),
                                        # dns_label="lbsub66e254209",
                                        route_table_id=oke_svclb_route_table.id,
                                        security_list_ids=[svclb_security_list.id],
                                        vcn_id=vcn.id,
                                        )
            return  lb_subnet
        except Exception as error:
            print("Loadbalancer subnet Creation failed " + str(error))

    def create_apiendpoint_subnet(self,config,vcn,oke_svclb_route_table,apiendpoint_security_list):
        try:
            apiendpoint_subnet = oci.core.Subnet("apiendpoint_subnet",
                                                 cidr_block=config.get('oke_apisubnet_cidr'),
                                                 compartment_id=config.get('compartment_ocid'),
                                                 # dhcp_options_id="ocid1.dhcpoptions.oc1.iad.aaaaaaaac7urxcbaietlipbfutlszxcgcvi5gqsadxqkmuu2u3mc5jwqzkhq",
                                                 display_name=config.get('oke_apisubnet_displayname'),
                                                 # dns_label="sub9ed679f8c",
                                                 route_table_id=oke_svclb_route_table.id,
                                                 security_list_ids=[apiendpoint_security_list.id],
                                                 vcn_id=vcn.id,
                                                 )
            return  apiendpoint_subnet


        except Exception as error:
            print("Apiendpoint subnet Creation failed " + str(error))






