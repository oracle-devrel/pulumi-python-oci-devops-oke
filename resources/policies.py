import os
import pulumi_oci as oci
from resources.random import random_string

class policies:
    def create_dgs(self,config,random_string_value):
        try:
            pulumi_devopsdg = oci.identity.DynamicGroup("pulumi_devopsdg",
                                                        compartment_id=os.environ['TF_VAR_tenancy_ocid'],
                                                        description=config.get('dg_description'),
                                                        matching_rule=f"Any {{ALL {{resource.type = 'devopsdeploypipeline', resource.compartment.id = '{config.get('compartment_ocid')}'}},ALL {{resource.type = 'devopsrepository', resource.compartment.id = '{config.get('compartment_ocid')}'}},ALL {{resource.type = 'devopsbuildpipeline', resource.compartment.id = '{config.get('compartment_ocid')}'}}}}",
                                                        name=f"{config.get('dg_name')}_{random_string_value}",
                                                        )
            return pulumi_devopsdg

        except Exception as error:
            print("DG Creation failed " + str(error))

    def create_policies(self,config,random_string_value):
        try:
            pulumi_devops_policies = oci.identity.Policy("pulumi_devops_policies",
                                                         compartment_id=config.get('compartment_ocid'),
                                                         description=config.get('policies_description'),
                                                         name=f"{config.get('policies_name')}_{random_string_value}",
                                                          statements=[
                                                             f"Allow group Administrators to manage devops-family in compartment id {config.get('compartment_ocid')}",
                                                             f"Allow group Administrators to manage all-artifacts in compartment id {config.get('compartment_ocid')}",
                                                             f"Allow dynamic-group {config.get('dg_name')}_{random_string_value} to manage all-resources in compartment id {config.get('compartment_ocid')}",
                                                          ],
                                                         )
            return pulumi_devops_policies

        except Exception as error:
            print("Policies Creation failed " + str(error))
