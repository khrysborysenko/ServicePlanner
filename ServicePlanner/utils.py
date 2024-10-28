from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from .models import ServiceHistory
from collections import Counter


def perform_clustering():
    service_histories = ServiceHistory.objects.all()

    X = [[history.service.id, history.client.id] for history in service_histories]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3)
    kmeans.fit(X_scaled)

    cluster_labels = kmeans.labels_

    for i, history in enumerate(service_histories):
        history.cluster_label = cluster_labels[i]
        history.save()


def recommend_services_for_customer(customer_id):
    customer_history = ServiceHistory.objects.filter(client_id=customer_id)

    if customer_history.exists():
        customer_cluster_label = customer_history.first().cluster_label

        similar_customers_history = ServiceHistory.objects.exclude(client_id=customer_id).filter(
            cluster_label=customer_cluster_label)

        recommended_services = []
        for history in similar_customers_history:
            recommended_services.append(history.service)

        recommended_services_count = Counter(recommended_services)

        recommended_services = sorted(recommended_services_count, key=recommended_services_count.get, reverse=True)

        return recommended_services
    else:
        return []
