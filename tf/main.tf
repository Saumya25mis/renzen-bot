provider "aws" {
    region = "us-west-1"
}

resource "aws_instance" "example" {
    ami = "ami-0e4d9ed95865f3b40"
    instance_type = "t2.micro"
    
    tags = {
        Name = "terraform-example"
    }
}