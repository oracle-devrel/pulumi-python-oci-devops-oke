import pulumi_oci as oci

class logs:
    def create_log_group(self,config):
        try:
            test_log_group = oci.logging.LogGroup("log_group",
                                                  compartment_id=config.get('compartment_ocid'),
                                                  display_name=f"{config.get('app_name_prefix')}_{config.get('loggroup_name')}",
                                                  description=config.get('loggroup_description'),
                                                 )
            return  test_log_group
        except Exception as error:
            print("Log creation failed " + str(error))

    def create_logs(self,config,log_group,devops_project):
        try:
            test_log = oci.logging.Log("logs",
                                       display_name=config.get('log_name'),
                                       log_group_id=log_group.id,
                                       log_type="SERVICE",
                                       configuration=oci.logging.LogConfigurationArgs(
                                           source=oci.logging.LogConfigurationSourceArgs(
                                               category="all",
                                               resource=devops_project.id,
                                               service="devops",
                                               source_type="OCISERVICE",
                                           ),
                                           compartment_id=config.get('compartment_ocid')
                                       ),
                                       is_enabled=True,
                                       retention_duration=int(config.get('log_retention_in_days')))
            return  test_log

        except exception as error:
            print("Log creation failed " + str(error))