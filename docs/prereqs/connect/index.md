# Connect to the Session Manager Workstation

To interact with the Aurora database cluster, you will use an <a href="https://aws.amazon.com/ec2/" target="_blank">Amazon EC2</a> Linux instance that acts like a workstation to interact with the AWS resources in the labs on this website. All necessary software packages and scripts have been installed and configured on this EC2 instance for you. To ensure a unified experience, you will be interacting with this workstation using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html" target="_blank">AWS Systems Manager Session Manager</a>. With Session Manager you can interact with your workstation directly from the management console, without the need to install any software on your own devices.

This lab contains the following tasks:

1. Connect to your workstation instance
2. Verify lab environment

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/)


## 1. Connect to your workstation instance

Open the <a href="https://us-west-2.console.aws.amazon.com/systems-manager/session-manager?region=us-west-2" target="_blank">Systems Manager: Session Manager service console</a>. Click the **Start session** button.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

<span class="image">![Start Session](1-start-session.png?raw=true)</span>

Please select an EC2 instance to establish a session with. The workstation is named `auroralab-mysql-workstation`, select it and click **Start session**.

<span class="image">![Connect Instance](1-connect-session.png?raw=true)</span>

If you see a black command like terminal screen and a prompt, you are now connected to the workstation. Type the following commands to ensure a consistent experience, and that the connection is successful:

```shell
sudo su -l ubuntu
```

!!! warning "Linux User Account"
    By default, Session Manager connects using the user account **ssm-user**. With the command above you are changing the user account to the **ubuntu** user account, which has the correct settings required for the labs. You can always check the current user account by typing ```whoami```, this will print the current user account.

    If you encounter errors accessing lab commands in subsequent labs, it is likely because the user account was not changed using the command above.


## 2. Verify lab environment

Let's make sure your workstation has been configured properly. Type the following command in the Session Manager command line:

```shell
tail -n1 /debug.log
```

You should see the output: `* bootstrap complete, rebooting`, if that is not the output you see, please wait a few more minutes and retry.

Once you have verified the environment is configured correctly, you can proceed to the next lab.
