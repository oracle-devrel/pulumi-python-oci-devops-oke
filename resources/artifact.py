import pulumi_oci as oci

class artifacts:
    def container_repo(self,config):
        try:
            container_repository = oci.artifacts.ContainerRepository("container_repo",
                                                                          compartment_id=config.get('compartment_ocid'),
                                                                          display_name=f"{config.get('app_name_prefix')}_{config.get('oci_containerrepo_displayname')}",
                                                                          is_public=config.get('oci_containerrepo_public'),
                                                                          # defined_tags={"version":config.get ('tag_version')}
                                                                          )
            return  container_repository
        except Exception as error:
            print("Error during container repo creation " + str(error))