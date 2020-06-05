# CloudPassage App for Splunk Enterprise

## Getting Started With the CloudPassage App

*   [How the CloudPassage App Works](#overview)
*   [Prerequisites](#prereq)
*   [A. Install the CloudPassage App](#install)
    *   [Get the App through the Splunk Apps](#gettheapp)
    *   [Get the App from the Halo Toolbox](#halotoolbox)
    *   [Verify the installation](#verify)
*   [B. Configure and Activate the CloudPassage App](#configure)
    *   [Retrieve and save your CloudPassage API key](#setup)
    *   [Configure the App in Splunk](#configsplunk)
*   [C. View Halo Events in Splunk](#haloevents)

This document describes the CloudPassage App for Splunk Enterprise and explains how to set up, configure, and get started using the App.

##How the CloudPassage App Works

The purpose of the CloudPassage App for Splunk Enterprise is to import Halo event data into Splunk Enterprise and allow it to be manipulated by Splunk users and displayed on Halo-specific pages within Splunk Enterprise. The App includes several Halo specific event display screens for reporting event results and summaries.

For event import, the App uses the script-based Modular Input tool. The Modular Input script retrieves event data from a CloudPassage Halo account and imports it into Splunk Enterprise for further processing.

**Retrieving events.** The script is designed to execute repeatedly, keeping Splunk up-to-date with Halo events as time passes and new events occur:
The first time the script runs, it by default retrieves all logged events within the past 90 days from a single Halo account. Then the script creates a file, writes the timestamp of the last-retrieved event in it, and saves it as a checkpoint. You may find the checkpoint file in `/Splunk/var/lib/splunk/modinputs`.
Every subsequent time the script runs, it retrieves only those events that were created after the timestamp stored in the checkpoint.
During any script run, if no new events have occurred since the last run, no events are retrieved or imported into Splunk.

**Output formats.** The script receives event data from Halo in Halo's native JavaScript Object Notation (JSON) format, which you can view in Splunk after the data has been imported.

**Authentication to the Halo API.** CloudPassage Halo requires the Modular Input script to pass a valid Halo API key pair in order to obtain event data. You can find the Halo API key pair in CloudPassage Halo Portal. We recommend using an auditor (read-only) API key pair with the necessary server group scope.

## Prerequisites

To get started, you must have the following:

* An active CloudPassage Halo subscription. If you don't have one, [Register for CloudPassage](https://portal.cloudpassage.com/registrations/new) to receive your credentials and further instructions by email.

* Access to your CloudPassage API key. Best practice is to create a new read-only key specifically for use with this script.

* Splunk Enterprise Server 8.0.3 or later. You can download Splunk Enterprise Server from [here](http://www.splunk.com/download).

### A. Install the CloudPassage App

You can obtain the CloudPassage app through Splunkbase or you can generate it from [github](https://github.com/cloudpassage/cloudpassage_splunk.git) repository.

### Get the App from Splunk Apps

To install the CloudPassage App for Splunk Enterprise, first log into Splunk Enterprise. After you have successfully logged in, click on the gear icon next to **Apps** on the top left of your screen then click on **Browse more apps**, this will take you to the Splunk Apps page.

![](42375ca8-fc8c-11e7-84c7-0a8f3fffaf98.png)

On the Splunk Apps page, search for “CloudPassage” to find the “CloudPassage App for Splunk Enterprise”. Click **Install** to install the app.

### Verify the Installation

Regardless of how you install the CloudPassage App, once you are successful it appears in the Splunk Enterprise dashboard, like this:

 ![](23d35946-fc8d-11e7-9d13-02a2abb09b24.png)

## B. Configure and Activate the CloudPassage App

After installing the CloudPassage App, configure it by obtaining required Halo information, specifying the Modular Input configuration settings in a configuration file, and entering additional data input settings within Splunk Enterprise. Once you have done that, execution of the App is automatic.

### Retrieve and save your CloudPassage API key

The Modular Input is a python script that makes calls to the CloudPassage API. The script is required to authenticate itself to Halo during every session; therefore, you (as a Halo user) need to make your CloudPassage API Key available to the script.

1. To retrieve your CloudPassage API key, log into the [CloudPassage Portal](https://portal.cloudpassage.com/login) and navigate to **Environment > Settings > Site Administration** and click the **API Keys** tab. (If you haven’t generated an API key yet, do so by clicking **Actions > New Api Key**.)

![](58bbdae6-fc8f-11e7-9f9e-02a2abb09b24.png)

If you do create an API key, we recommend that, as a best practice, you create a read-only key (audtior). A read-only key is all that you need to be able to retrieve Halo event data.

 ![](6008192c-fc8f-11e7-9868-02a2abb09b24.png)

2. Retrieve both the **Key ID** and the **Secret Key** values for the API key. Click **Show** for your key on the **API Keys** tab to display both values.

## Create cloudpassage Index
All events will be written to an index named **cloudpassage**. Make sure to create the index via **the Splunk GUI** before activating the CloudPassage App. To create the cloudpassage index follow these steps:
1. Login to Splunk Enterprise and from **Settings** menu navigate to **data** section and select **Indexes**.
2. In the indexes page click on **New Index** button in the top right corner of the screen.
3. In the **index name** input field, you must enter "cloudpassage", and for the **app** dropdown list select “CloudPassage Splunk”, all other parameters is up to the user to decide. Then click **save** button
4. The **cloudpassage** index now created.

## Configure the App in Splunk

Now integrate your installed CloudPassage App into Splunk Enterprise.

Log into your Splunk Enterprise installation. Choose **Data Inputs** from the **Settings** menu.

![](63745e1c-fc90-11e7-a331-0a8f3fffaf98.png)

Click on **CloudPassage Splunk Connector** dialog box opens.

![](c55519ce-fc8f-11e7-bf03-02a2abb09b24.png)

You add new types of data to Splunk Enterprise by telling it about them. There are a number of ways you can specify a data input, either in terms of its type or by its source. The Modular Input script is a source that collects data for Splunk by connecting to the CloudPassage Grid and using the Halo Event API. That is the source type that you will select.
Click on the **Add new** dialog box opens:

![](b4309aa6-fc8f-11e7-bb93-02a2abb09b24.png)

Fill in these fields:

![](be3f8ad4-fc8f-11e7-bb93-02a2abb09b24.png)

* **Name:** Enter a display name for your App, such as "cphalo". This name appears on the App's data input summary page.
* **CloudPassage Halo API Key:** Copy your saved Halo API key ID and paste it into this field.
* **CloudPassage Halo API Secret:** Copy your saved Halo API key secret and paste it into this field.
* **Starting Date/Time:** Optionally enter the starting date-time of events to be retrieved from your Halo account. Use ISO-8601 format; for example 2013-09-19T17:34:28.808886Z. All events newer than this date-time will be retrieved the first time the script runs; on each subsequent run, only events newer than the newest previously retrieved event will be retrieved.Putting a value in this field is optional; if you leave it blank, the first execution of the script will retrieve all defined events from your Halo account within 90 days prior.
Please Note:
  * If checkpoint exists, it will take precedence. You can find the checkpoint in `/Splunk/var/lib/splunk/modinputs`.
  * CloudPassage Halo has a 90 days data retention period.
* **API Hostname:** By default this is set to `api.cloudpassage.com`. If your CloudPassage API hostname is different from the default setting, please specify here.
* **Proxy Host:** Copy your proxy host ip address and paste it into this field. (Optional)
* **Proxy Port:** Copy your proxy port and paste it into this field. (Optional)
* **API concurrency:** Concurrency number.
* **Dedicated Log File Name:** the name of the dedicated log file.
* **Set sourcetype.** Choose "Manual".
* **Select source type from list.** Select the source type value that you specified in the Splunk props.conf file (for example, [cp_halo]; see Set up props.conf).
* **Set the destination index for this source:** select **cloudpassage** index from the list.
After filling in this information, Click **Save** button.

When it has finished adding the new data source, Splunk displays a success message:
You're done! The Modular Input script is now running, automatically providing events to Splunk for indexing.

Note:
* You can find default **Splunk log** file here: “\Splunk\var\log\splunk\splunkd.log”
* For **dedicated log** file: “\Splunk\var\log\splunk\[Dedicated Log File Name].log”

###C. View Halo Events in Splunk

The CloudPassage App provides several interactive pages that allow you to view and manipulate your Halo data from many different perspectives. Once the script runs successfully and is incorporating event data into Splunk, you will see Halo events such as the following appear in your CloudPassage App within Splunk Enterprise.You're done! The Modular Input script is now running, automatically providing events to Splunk for indexing.

### **The Halo Dashboard page:**

![120510](675533c6-6900-11e3-b4de-005056ad5c72.png)

### **The Violation Dashboard page:**

![120509](6756e806-6900-11e3-b4de-005056ad5c72.png)