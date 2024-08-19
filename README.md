# gcp-dataproc-workflow

## Description of Services Used in GCP

## Apache Spark
Apache Spark is an open-source unified analytics engine for large-scale data processing. It is known for its speed, ease of use, and sophisticated analytics capabilities. Spark provides an interface for programming entire clusters with implicit data parallelism and fault tolerance, making it suitable for a wide variety of big data applications.

## Google Dataproc
Google Dataproc is a fully managed cloud service that simplifies running Apache Spark and Apache Hadoop clusters in the Google Cloud environment. It allows users to easily process large datasets and integrates seamlessly with other Google Cloud services such as Cloud Storage. Dataproc is designed to make big data processing fast and efficient while minimizing operational overhead.

## Cloud Storage
Google Cloud Storage is a scalable and secure object storage service for storing large amounts of unstructured data. It offers high availability and strong global consistency, making it suitable for a wide range of scenarios, such as data backups, big data analytics, and content distribution.

## Workflow Templates
Workflow templates in Google Cloud allow you to define and manage complex workflows that automate interactions between different cloud services. This feature simplifies the process of building, scheduling, and executing intricate workflows, ensuring better management of resources and tasks.

## Cloud Scheduler
Google Cloud Scheduler is a fully managed cron job service that allows you to run arbitrary functions at specified times without needing to manage the infrastructure. It is useful for automating tasks such as running reports, triggering workflows, and executing other scheduled jobs.

## CI/CD Process with GitHub Actions
Incorporating a CI/CD pipeline using GitHub Actions involves automating the build, test, and deployment processes of your applications. For this project, GitHub Actions simplifies the deployment of code and resources to Google Cloud. This automation leverages GitHub's infrastructure to trigger workflows based on events such as code pushes, ensuring that your applications are built and deployed consistently and accurately each time code changes are made.

## GitHub Secrets and Configuration
Utilizing secrets in GitHub Actions is vital for maintaining security during the deployment process. Secrets allow you to store sensitive information such as API keys, passwords, and service account credentials securely. By keeping this sensitive data out of your source code, you minimize the risk of leaks and unauthorized access.


1. GCP_BUCKET_BIGDATA_FILES
    1. Secret used to store the name of the cloud storage
   
2. GCP_BUCKET_DATALAKE
    1. Secret used to store the name of the cloud storage

3. GCP_BUCKET_DATAPROC
    1. Secret used to store the name of the cloud storage

5. GCP_SERVICE_ACCOUNT

4. GCP_SA_KEY
    1. Secret used to store the value of the service account key. For this project, the default service key was used. 

6. PROJECT_ID
    1. Secret used to store the project id value

###Creating a GCP service account key

To create computing resources in any cloud, in an automated or programmatic way, it is necessary to have an access key.
In the case of GCP, we use an access key linked to a service account, for the project the default account was used.

1. In GCP Console, access :
   1. IAM &Admin
   2. Service accounts
   3. Select default service account, default name is something like **Compute Engine default service account**
   4. In selected service account, menu **KEYS**, 
       1. **ADD KEY**, **Create new Key**, Key Type **json**
       2. Download the key file, use the content as key value in your secret in github

![GCP service account key](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ua188978d64xi4o6php2.png)

For more details, access:
https://cloud.google.com/iam/docs/keys-create-delete

### Creating github secret

1. To create a new secret:
    1. In project repository, menu **Settings** 
    2. **Security**, 
    3. **Secrets and variables**,click in access **Action**
    4. **New repository secret**, type a **name** and **value** for secret.

![github secret creation](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/i45cicz0q89ije7j70yf.png)

For more details , access :
https://docs.github.com/pt/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions

## Deploying the project
Every time a push to the **main** branch happens, github actions will be triggered,
running the yml script.
the yml script contains 3 jobs which are explained in more detail below, but basically
github actions uses the credentials of the service account with rights to create 
computing resources, if you authenticate to GCP, perform the steps described in the yml file

```yml
on:
    push:
        branchs: [main]
```


## Workflow File YAML Explanation

### Environments Needed
Here's a brief explanation of the environment variables needed in your workflows based on the YAML file you provided:

```yaml
env:
    BRONZE_DATALAKE_FILES: bronze
    TRANSIENT_DATALAKE_FILES: transient
    BUCKET_DATALAKE_FOLDER: transient
    BUCKET_BIGDATA_JAR_FOLDER: jars
    BUCKET_BIGDATA_PYSPARK_FOLDER: scripts
    PYSPARK_INGESTION_SCRIPT : ingestion_csv_to_delta.py 
    REGION: us-east1
    ZONE: us-east1-b
    DATAPROC_CLUSTER_NAME : dataproc-bigdata-multi-node-cluster
    DATAPROC_WORKER_TYPE : n2-standard-2
    DATAPROC_MASTER_TYPE : n2-standard-2
    DATAPROC_NUM_WORKERS : 2
    DATAPROC_IMAGE_VERSION : 2.1-debian11
    DATAPROC_WORKER_NUM_LOCAL_SSD: 1
    DATAPROC_MASTER_NUM_LOCAL_SSD: 1
    DATAPROC_MASTER_BOOT_DISK_SIZE: 32   
    DATAPROC_WORKER_DISK_SIZE: 32
    DATAPROC_MASTER_BOOT_DISK_TYPE: pd-balanced
    DATAPROC_WORKER_BOOT_DISK_TYPE: pd-balanced
    DATAPROC_COMPONENTS: JUPYTER
    DATAPROC_WORKFLOW_NAME: departments_etl
    DATAPROC_WORKFLOW_INGESTION_STEP_NAME: ingestion_countries_csv_to_delta 
    JAR_LIB1 : delta-core_2.12-2.3.0.jar
    JAR_LIB2 : delta-storage-2.3.0.jar 
    APP_NAME : 'countries_ingestion_csv_to_delta'
    SUBJECT : departments
    STEP1 : countries
    STEP2 : departments
    STEP3 : employees
    STEP4 : jobs
    TIME_ZONE : America/Sao_Paulo
    SCHEDULE : "20 12 * * *"
    SCHEDULE_NAME : schedule_departments_etl
    SERVICE_ACCOUNT_NAME : dataproc-account-workflow
    CUSTOM_ROLE : WorkflowCustomRole
    STEP1_NAME : step_countries
    STEP2_NAME : step_departments
    STEP3_NAME : step_employees
    STEP4_NAME : step_jobs
```

### **Deploy Buckets Job**
This job is responsible for creating three Google Cloud Storage buckets: one for transient files, one for jar files, and one for PySpark scripts. It checks if each bucket already exists before attempting to create them. Additionally, it uploads specified files into these buckets to prepare for later processing.


```yaml
jobs:
  deploy-buckets:
    runs-on: ubuntu-22.04
    timeout-minutes: 10
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Authorize GCP
      uses: 'google-github-actions/auth@v2'
      with:
        credentials_json:  ${{ secrets.GCP_SA_KEY }}

    # Step to Create GCP Bucket 
    - name: Create Google Cloud Storage - files
      run: |-
        if ! gsutil ls -p ${{ secrets.PROJECT_ID }} gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }} &> /dev/null; \
          then \
            gcloud storage buckets create gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }} --default-storage-class=nearline --location=${{ env.REGION }}
          else
            echo "Cloud Storage : gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}  already exists" ! 
          fi

    # Step to Create GCP Bucket 
    - name: Create Google Cloud Storage - dataproc
      run: |-
        if ! gsutil ls -p ${{ secrets.PROJECT_ID }} gs://${{ secrets.GCP_BUCKET_DATAPROC }} &> /dev/null; \
          then \
            gcloud storage buckets create gs://${{ secrets.GCP_BUCKET_DATAPROC }} --default-storage-class=nearline --location=${{ env.REGION }}
          else
            echo "Cloud Storage : gs://${{ secrets.GCP_BUCKET_DATAPROC }}  already exists" ! 
          fi

    # Step to Create GCP Bucket 
    - name: Create Google Cloud Storage - datalake
      run: |-
        if ! gsutil ls -p ${{ secrets.PROJECT_ID }} gs://${{ secrets.GCP_BUCKET_DATALAKE }} &> /dev/null; \
          then \
            gcloud storage buckets create gs://${{ secrets.GCP_BUCKET_DATALAKE }} --default-storage-class=nearline --location=${{ env.REGION }}
          else
            echo "Cloud Storage : gs://${{ secrets.GCP_BUCKET_DATALAKE }}  already exists" ! 
          fi

    # Step to Upload the file to GCP Bucket - transient files
    - name: Upload transient files to Google Cloud Storage
      run: |-
        TARGET=${{ env.TRANSIENT_DATALAKE_FILES }}
        BUCKET_PATH=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}    
        gsutil cp -r $TARGET gs://${BUCKET_PATH}


    # Step to Upload the file to GCP Bucket - jar files
    - name: Upload jar files to Google Cloud Storage
      run: |-
        TARGET=${{ env.BUCKET_BIGDATA_JAR_FOLDER }}
        BUCKET_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}
        gsutil cp -r $TARGET gs://${BUCKET_PATH}

    # Step to Upload the file to GCP Bucket - pyspark files
    - name: Upload pyspark files to Google Cloud Storage
      run: |-
        TARGET=${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}
        BUCKET_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}
        gsutil cp -r $TARGET gs://${BUCKET_PATH}

    # Step to create dataproc cluster
    - name: Upload pyspark files to Google Cloud Storage
      run: |-
        TARGET=${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}
        BUCKET_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}
        gsutil cp -r $TARGET gs://${BUCKET_PATH}
```

### **Explanation:** 
This job begins by checking out the code and authorizing Google Cloud credentials. It then checks for the existence of three specified Cloud Storage buckets—one for transient files, one for JAR files, and one for PySpark scripts. If these buckets do not exist, it creates them with gcloud. Finally, it uploads the relevant files to the corresponding buckets using gsutil.


## **Deploy Dataproc Workflow Template Job**
This job deploys a Dataproc workflow template in Google Cloud. It begins by checking if the workflow template already exists; if not, it creates one. It also sets up a managed Dataproc cluster with specific configurations such as the machine types and number of workers. Subsequently, it adds various steps (jobs) to the workflow template to outline the processing tasks for data ingestion.

Code Snippet:

```yml
  deploy-dataproc-workflow-template:
    needs: [deploy-buckets]
    runs-on: ubuntu-22.04
    timeout-minutes: 10

    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Authorize GCP
      uses: 'google-github-actions/auth@v2'
      with:
        credentials_json:  ${{ secrets.GCP_SA_KEY }}

    - name: Create Dataproc Workflow
      run: |-  
        if ! gcloud dataproc workflow-templates list --region=${{ env.REGION}} | grep -i ${{ env.DATAPROC_WORKFLOW_NAME}} &> /dev/null; \
          then \
            gcloud dataproc workflow-templates create ${{ env.DATAPROC_WORKFLOW_NAME }} --region ${{ env.REGION }}
          else
            echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME }} already exists" ! 
          fi

    - name: Create Dataproc Managed Cluster
      run: >       
        gcloud dataproc workflow-templates set-managed-cluster ${{ env.DATAPROC_WORKFLOW_NAME }} 
        --region ${{ env.REGION }} 
        --zone ${{ env.ZONE }} 
        --image-version ${{ env.DATAPROC_IMAGE_VERSION }} 
        --master-machine-type=${{ env.DATAPROC_MASTER_TYPE }} 
        --master-boot-disk-type ${{ env.DATAPROC_MASTER_BOOT_DISK_TYPE }} 
        --master-boot-disk-size ${{ env.DATAPROC_MASTER_BOOT_DISK_SIZE }} 
        --worker-machine-type=${{ env.DATAPROC_WORKER_TYPE }} 
        --worker-boot-disk-type ${{ env.DATAPROC_WORKER_BOOT_DISK_TYPE }}
        --worker-boot-disk-size ${{ env.DATAPROC_WORKER_DISK_SIZE }} 
        --num-workers=${{ env.DATAPROC_NUM_WORKERS }} 
        --cluster-name=${{ env.DATAPROC_CLUSTER_NAME }} 
        --optional-components ${{ env.DATAPROC_COMPONENTS }} 
        --service-account=${{ env.GCP_SERVICE_ACCOUNT }}

    - name: Add Job Ingestion countries to Workflow
      run: |-
        if gcloud dataproc workflow-templates list --region=${{ env.REGION}} | grep -i ${{ env.DATAPROC_WORKFLOW_NAME}} &> /dev/null; \
          then \
            
            if gcloud dataproc workflow-templates describe ${{ env.DATAPROC_WORKFLOW_NAME}} --region=${{ env.REGION}} | grep -i ${{ env.STEP1_NAME  }} &> /dev/null; \
            then \
              echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME }} already has step : ${{ env.STEP1_NAME  }} " ! 
            else
              PYSPARK_SCRIPT_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}/${{ env.PYSPARK_INGESTION_SCRIPT }}
              JARS_PATH=gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB1 }}
              JARS_PATH=${JARS_PATH},gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB2 }}
              TRANSIENT=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}/${{ env.SUBJECT }}/${{ env.STEP1 }}
              BRONZE=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BRONZE_DATALAKE_FILES }}/${{ env.SUBJECT }}/${{ env.STEP1 }}

              gcloud dataproc workflow-templates add-job pyspark gs://${PYSPARK_SCRIPT_PATH} \
              --workflow-template ${{ env.DATAPROC_WORKFLOW_NAME }}  \
              --step-id ${{env.STEP1_NAME }} \
              --region ${{ env.REGION }} \
              --jars ${JARS_PATH} \
              -- --app_name=${{ env.APP_NAME }}${{ env.STEP1 }} --bucket_transient=gs://${TRANSIENT} \
              --bucket_bronze=gs://${BRONZE}
            fi
        else
          echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME}} not exists" ! 
        fi        

    - name: Add Job Ingestion departments to Workflow
      run: |-
        if gcloud dataproc workflow-templates list --region=${{ env.REGION}} | grep -i ${{ env.DATAPROC_WORKFLOW_NAME}} &> /dev/null; \
          then \
            if gcloud dataproc workflow-templates describe ${{ env.DATAPROC_WORKFLOW_NAME}} --region=${{ env.REGION}} | grep -i ${{ env.STEP2_NAME }} &> /dev/null; \
            then \
              echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME }} already has step : ${{ env.STEP2_NAME  }} " ! 
            else
              PYSPARK_SCRIPT_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}/${{ env.PYSPARK_INGESTION_SCRIPT }}
              JARS_PATH=gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB1 }}
              JARS_PATH=${JARS_PATH},gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB2 }}
              TRANSIENT=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}/${{ env.SUBJECT }}/${{ env.STEP2 }}
              BRONZE=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BRONZE_DATALAKE_FILES }}/${{ env.SUBJECT }}/${{ env.STEP2 }}

              gcloud dataproc workflow-templates add-job pyspark gs://${PYSPARK_SCRIPT_PATH} \
              --workflow-template ${{ env.DATAPROC_WORKFLOW_NAME }}  \
              --step-id ${{ env.STEP2_NAME }} \
              --start-after ${{ env.STEP1_NAME }} \
              --region ${{ env.REGION }} \
              --jars ${JARS_PATH} \
              -- --app_name=${{ env.APP_NAME }}${{ env.STEP2 }} --bucket_transient=gs://${TRANSIENT} \
              --bucket_bronze=gs://${BRONZE}
            fi
        else
          echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME}} not exists" ! 
        fi
       

    - name: Add Job Ingestion employees to Workflow
      run: |-
        if gcloud dataproc workflow-templates list --region=${{ env.REGION}} | grep -i ${{ env.DATAPROC_WORKFLOW_NAME}} &> /dev/null; \
          then \
            if gcloud dataproc workflow-templates describe ${{ env.DATAPROC_WORKFLOW_NAME}} --region=${{ env.REGION}} | grep -i ${{ env.STEP3_NAME }} &> /dev/null; \
            then \
              echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME }} already has step : ${{ env.STEP3_NAME }} " ! 
            else
              PYSPARK_SCRIPT_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}/${{ env.PYSPARK_INGESTION_SCRIPT }}
              JARS_PATH=gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB1 }}
              JARS_PATH=${JARS_PATH},gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB2 }}
              TRANSIENT=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}/${{ env.SUBJECT }}/${{ env.STEP2 }}
              PYSPARK_SCRIPT_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}/${{ env.PYSPARK_INGESTION_SCRIPT }}
              JARS_PATH=gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB1 }}
              JARS_PATH=${JARS_PATH},gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB2 }}
              TRANSIENT=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}/${{ env.SUBJECT }}/${{ env.STEP3 }}
              BRONZE=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BRONZE_DATALAKE_FILES }}/${{ env.SUBJECT }}/${{ env.STEP3 }}

              gcloud dataproc workflow-templates add-job pyspark gs://${PYSPARK_SCRIPT_PATH} \
              --workflow-template ${{ env.DATAPROC_WORKFLOW_NAME }}  \
              --step-id ${{ env.STEP3_NAME }} \
              --start-after ${{ env.STEP1_NAME }},${{ env.STEP2_NAME }} \
              --region ${{ env.REGION }} \
              --jars ${JARS_PATH} \
              -- --app_name=${{ env.APP_NAME }}${{ env.STEP3 }} --bucket_transient=gs://${TRANSIENT} \
              --bucket_bronze=gs://${BRONZE}
            fi
        else
          echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME}} not exists" ! 
        fi

    - name: Add Job Ingestion Jobs to Workflow
      run: |-
        if gcloud dataproc workflow-templates list --region=${{ env.REGION}} | grep -i ${{ env.DATAPROC_WORKFLOW_NAME}} &> /dev/null; \
          then \
            if gcloud dataproc workflow-templates describe ${{ env.DATAPROC_WORKFLOW_NAME}} --region=${{ env.REGION}} | grep -i ${{ env.STEP4_NAME }} &> /dev/null; \
            then \
              echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME }} already has step : ${{ env.STEP4_NAME }} " ! 
            else
              PYSPARK_SCRIPT_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}/${{ env.PYSPARK_INGESTION_SCRIPT }}
              JARS_PATH=gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB1 }}
              JARS_PATH=${JARS_PATH},gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB2 }}
              TRANSIENT=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}/${{ env.SUBJECT }}/${{ env.STEP2 }}
              PYSPARK_SCRIPT_PATH=${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_PYSPARK_FOLDER }}/${{ env.PYSPARK_INGESTION_SCRIPT }}
              JARS_PATH=gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB1 }}
              JARS_PATH=${JARS_PATH},gs://${{ secrets.GCP_BUCKET_BIGDATA_FILES }}/${{ env.BUCKET_BIGDATA_JAR_FOLDER }}/${{ env.JAR_LIB2 }}
              TRANSIENT=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BUCKET_DATALAKE_FOLDER }}/${{ env.SUBJECT }}/${{ env.STEP4 }}
              BRONZE=${{ secrets.GCP_BUCKET_DATALAKE }}/${{ env.BRONZE_DATALAKE_FILES }}/${{ env.SUBJECT }}/${{ env.STEP4 }}

              gcloud dataproc workflow-templates add-job pyspark gs://${PYSPARK_SCRIPT_PATH} \
              --workflow-template ${{ env.DATAPROC_WORKFLOW_NAME }}  \
              --step-id ${{ env.STEP4_NAME }} \
              --start-after ${{ env.STEP1_NAME }},${{ env.STEP2_NAME }},${{ env.STEP3_NAME }} \
              --region ${{ env.REGION }} \
              --jars ${JARS_PATH} \
              -- --app_name=${{ env.APP_NAME }}${{ env.STEP4 }} --bucket_transient=gs://${TRANSIENT} \
              --bucket_bronze=gs://${BRONZE}
            fi
        else
          echo "Workflow Template : ${{ env.DATAPROC_WORKFLOW_NAME}} not exists" ! 
        fi
```

### **Explanation**
This job follows a systematic approach to deploying a Dataproc workflow template. It first checks if the workflow template exists and creates it if it does not. Next, a managed Dataproc cluster is configured with specified properties (e.g., number of workers, machine type). The job also adds specified steps for data ingestion tasks to the workflow template, detailing how data should be processed. The remaining steps for Add Job are structured similarly, each focusing on different data ingestion tasks within the workflow.


Deploy Cloud Schedule Job
This job sets up a scheduling mechanism using Google Cloud Scheduler. It creates a service account specifically for the scheduled job, defines a custom role with specific permissions, and binds the custom role to the service account. Finally, it creates the cloud schedule to trigger the execution of the workflow at defined intervals.

```yml
    deploy-cloud-schedule:
    needs: [deploy-buckets, deploy-dataproc-workflow-template]
    runs-on: ubuntu-22.04
    timeout-minutes: 10

    steps:
    - name: Checkout
      uses: actions/checkout@v4
    
    - name: Authorize GCP
      uses: 'google-github-actions/auth@v2'
      with:
        credentials_json:  ${{ secrets.GCP_SA_KEY }}
    
    # Step to Authenticate with GCP
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      with:
        version: '>= 363.0.0'
        project_id: ${{ secrets.PROJECT_ID }}

    # Step to Configure Docker to use the gcloud command-line tool as a credential helper
    - name: Configure Docker
      run: |-
        gcloud auth configure-docker


    - name: Create service account
      run: |-
      
        if ! gcloud iam service-accounts list | grep -i ${{ env.SERVICE_ACCOUNT_NAME}} &> /dev/null; \
          then \
            gcloud iam service-accounts create ${{ env.SERVICE_ACCOUNT_NAME }} \
            --display-name="scheduler dataproc workflow service account"
          fi
    - name: Create Custom role for service account
      run: |-
        if ! gcloud iam roles list --project ${{ secrets.PROJECT_ID }} | grep -i ${{ env.CUSTOM_ROLE }} &> /dev/null; \
          then \
            gcloud iam roles create ${{ env.CUSTOM_ROLE }} --project ${{ secrets.PROJECT_ID }} \
            --title "Dataproc Workflow template scheduler" --description "Dataproc Workflow template scheduler" \
            --permissions "dataproc.workflowTemplates.instantiate,iam.serviceAccounts.actAs" --stage ALPHA
          fi    

    - name: Add the custom role for service account
      run: |-
        gcloud projects add-iam-policy-binding ${{secrets.PROJECT_ID}} \
        --member=serviceAccount:${{env.SERVICE_ACCOUNT_NAME}}@${{secrets.PROJECT_ID}}.iam.gserviceaccount.com \
        --role=projects/${{secrets.PROJECT_ID}}/roles/${{env.CUSTOM_ROLE}}

    - name: Create cloud schedule for workflow execution
      run: |-
        if ! gcloud scheduler jobs list --location ${{env.REGION}} | grep -i ${{env.SCHEDULE_NAME}} &> /dev/null; \
          then \
            gcloud scheduler jobs create http ${{env.SCHEDULE_NAME}} \
            --schedule="30 12 * * *" \
            --description="Dataproc workflow " \
            --location=${{env.REGION}} \
            --uri=https://dataproc.googleapis.com/v1/projects/${{secrets.PROJECT_ID}}/regions/${{env.REGION}}/workflowTemplates/${{env.DATAPROC_WORKFLOW_NAME}}:instantiate?alt=json \
            --time-zone=${{env.TIME_ZONE}} \
            --oauth-service-account-email=${{env.SERVICE_ACCOUNT_NAME}}@${{secrets.PROJECT_ID}}.iam.gserviceaccount.com
          fi

```

### **Explanation**
In this job, a service account is created specifically for handling the scheduled workflow execution. It also defines a custom role that grants the necessary permissions for the service account to instantiate the workflow template. This custom role is then associated with the service account to ensure it has the required permissions. Finally, the job creates a cloud schedule that triggers the workflow execution at predetermined times, ensuring automated execution of the data processing workflow.

## **Resources created after deploy process**

### **Dataproc Workflow Template**

When accessing the dataproc service, we can, among other options, check the Workflow tab the execution of workflows, workflow details and their details.

![dataproc workflow temmplate 1](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/l8c09t53cv125vjx89gd.jpeg)

By selecting the workflow created, it is possible to check the cluster used in processing 
and the steps that make up the workflow, in addition to dependencies between the steps.

![dataproc workflow temmplate 2](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/msalytbi3oc92ofwj9z0.jpeg)

In the dataproc service, it is possible to check the execution of each job, execution status and other details, in the case of Workflow templates it is possible to check each execution, with details regarding the execution of steps in the workflow template, as shown in the image below

![dataproc workflow temmplate 3](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/r1aps48bpuu9hpsztbtb.jpeg)

### **Cloud Scheduler**

By accessing the cloud schedule service, the service created by the deploy appears, in the image below,
It is possible to include the status details of the last run, the schedule, which execution target or other details.

![cloud scheduler](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7k92sfeqnxwynlr200lj.jpeg)

### **Cloud Storage**


![cloud storage](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/uulc45ddeqy0ucggsclt.jpeg)

alla
![cloud storage files](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/wpm81m10u0gjt401dftw.jpeg)

###Conclusion
Data pipelines are essential elements in the world of data processing, although there are specialized and feature-rich tools such as Azure Data Factory and Apache Airflow, there are simpler options that are often interesting in certain scenarios, leaving it up to the data and architecture team to define the tool.
most appropriate for the moment.