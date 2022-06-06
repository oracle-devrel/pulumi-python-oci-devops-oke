import pulumi

def outputs(config):

    pulumi.export("Stack","OCI Devops with OKE ")
    pulumi.export("Kubeconfig" ,"generated/kubeconfig")
    pulumi.export("Authors","Made with \u2764 by Oracle Developers")