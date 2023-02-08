# Mô tả quy trình CI/CD để deploy api này lên k8s. 
## - Các stages: 
    + Build image 
    + Push image to Registry 
    + Deploy to K8S cluster 

1. Build image và gắn tag cho Image, thường sẽ dùng BUILD_NUMBER hay CI_PIPELINE_ID, CI_COMMIT_SHA cho gitlabCI
    - Run command: `docker build -t phanminhlam/update-asg:$(BUILD_NUMBER) .`
  
2. Push image to Registry. Dùng user, password hoặc dùng dockerconfigjson để login vào registry.
    - Run command: `docker login -u username -p password`
    - Run command: `docker push phanminhlam/update-asg:$(BUILD_NUMBER)`

3. Deploy to K8S cluster: Trước khi deploy set up Credential để Jenkins có thể thực hiện thao tác trên k8s cluster và deploy image trước 1 lần lên deployment, vì sau đây dùng lệnh `kubectl rollout restart` để cập nhật image mới cho deployment. 

    - `kubectl -n namespace rollout restart deployment update-asg-deployment`
    
    - `kubectl -n namespace rollout status deployment update-asg-deployment` # Wait for migrations