# Connect to the Session Manager Workstation

To interact with the Aurora database cluster, you will use an <a href="https://aws.amazon.com/ec2/" target="_blank">Amazon EC2</a> Linux instance that acts like a workstation to interact with the AWS resources in the labs on this website. All necessary software packages and scripts have been installed and configured on this EC2 instance for you. To ensure a unified experience, you will be interacting with this workstation using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html" target="_blank">AWS Systems Manager Session Manager</a>. With Session Manager you can interact with your workstation directly from the management console, without the need to install any software on your own devices.

This lab contains the following tasks:

1. Connect to your workstation instance
2. Verify lab environment

This lab requires the following prerequisites:

* [Deploy Environment](/prereqs/environment/)


## 1. Connect to your workstation instance

Open the <a href="https://us-west-2.console.aws.amazon.com/systems-manager/session-manager?region=us-west-2" target="_blank">Systems Manager: Session Manager service console</a>. Click **Configure Preferences**.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

!!! warning "Console Differences"
    The introduction screen with the **Configure Preferences** and **Start Session** buttons only appears when you start using Session Manager for the first time in a new account. Once you have started using this service the console will display the session listing view instead, and the preferences page is accessible by clicking on the **Preferences** tab. From there, click the **Edit** button if you wish to change settings.

<span class="image">![Session Manager](1-session-manager.png?raw=true)</span>

Check the box next to **Enable Run As support for Linux instances**, and enter `ubuntu` in the text field. This will instruct Session Manager to connect to the workstation using the `ubuntu` operating system user account. Click **Save**.

!!! note
    You will only need to set the preferences once for the purposes of the labs. However, if you use Session Manager for other use cases you may need to revert the changes back as needed.

<span class="image">![Session Preferences](1-session-prefs.png?raw=true)</span>

Next, navigate to the **Sessions** tab, and click the **Start session** button.

<span class="image">![Start Session](1-start-session.png?raw=true)</span>

Please select an EC2 instance to establish a session with. The workstation is named `labstack-bastion-host`, select it and click **Start session**.

<span class="image">![Conenct Instance](1-connect-session.png?raw=true)</span>

If you see a black command like terminal screen and a prompt, you are now connected to the workstation. Type the following commands to ensure a consistent experience, and that the connection is successful:

```
bash
cd ~
```

## 2. Verify lab environment

Let's make sure your workstation has been configured properly. Type the following command in the Session Manager command line:

```
tail -n1 /debug.log
```

You should see the output: `* bootstrap complete, rebooting`, if that is not the output you see, please wait a few more minutes and retry.

Once you have verified the environment is configured correctly, you can proceed to the next lab.
