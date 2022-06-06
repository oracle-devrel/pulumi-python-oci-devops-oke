import pulumi_oci as oci

class notification:

    def create_notification_topic(self,config):
        try:
            test_notification_topic = oci.ons.NotificationTopic("notification_topic",
                                                                compartment_id=config.get('compartment_ocid'),
                                                                description=config.get('notification_description'),
                                                                name=f"{config.get('app_name_prefix')}_{config.get('notification_topic_name')}",
                                                                freeform_tags={}

                                                                )
            return test_notification_topic
        except Exception as error:
            print( "Notification error " + str(error))
