#!/usr/bin/env python3
"""
AnalytiX – Canary Deployment Generator
=================================================
Generates canary traffic-split Ingress manifests using NGINX annotations.

Usage:
    python canary_deploy.py --service query-service --weight 10 --version 1.1.0

This creates a secondary deployment receiving X% of traffic while
the stable version handles the rest.
"""

import argparse
import os
import sys


def generate_canary(service_name: str, port: int, weight: int, version: str) -> str:
    """Generate canary deployment + service + ingress patch."""
    canary_name = f"{service_name}-canary"
    image = f"discover-{service_name}:{version}"

    return f"""# =============================================================================
# Canary Deployment: {service_name} @ {version} ({weight}% traffic)
# Apply with: kubectl apply -f {canary_name}.yaml
# =============================================================================
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {canary_name}
  namespace: genquantaa
  labels:
    app: {service_name}
    track: canary
    version: "{version}"
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {service_name}
      track: canary
  template:
    metadata:
      labels:
        app: {service_name}
        track: canary
        version: "{version}"
    spec:
      containers:
        - name: {service_name}
          image: {image}
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: {port}
          env:
            - name: PORT
              value: "{port}"
            - name: ENVIRONMENT
              value: "production-canary"
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: {port}
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /readyz
              port: {port}
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: {canary_name}
  namespace: genquantaa
  labels:
    app: {service_name}
    track: canary
spec:
  selector:
    app: {service_name}
    track: canary
  ports:
    - name: http
      protocol: TCP
      port: {port}
      targetPort: {port}
  type: ClusterIP
---
# Canary Ingress – routes {weight}% of traffic to canary version
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {canary_name}-ingress
  namespace: genquantaa
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "{weight}"
spec:
  rules:
    - host: api.genquantaa.com
      http:
        paths:
          - path: /api/v1/{service_name.replace('-service', '').replace('-', '/')}
            pathType: Prefix
            backend:
              service:
                name: {canary_name}
                port:
                  number: {port}
---
# To promote canary to stable:
#   kubectl set image deployment/{service_name} {service_name}={image}
#   kubectl delete -f {canary_name}.yaml
#
# To roll back canary:
#   kubectl delete -f {canary_name}.yaml
"""


SERVICE_PORTS = {
    "auth-service": 8001,
    "metadata-service": 8002,
    "query-service": 8003,
    "cheminformatics-service": 8004,
    "connector-service": 8005,
    "audit-service": 8006,
    "lineage-service": 8007,
    "bioinformatics-service": 8008,
    "workflow-service": 8009,
    "ai-service": 8010,
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate canary deployment manifests")
    parser.add_argument("--service", required=True, choices=list(SERVICE_PORTS.keys()))
    parser.add_argument("--weight", type=int, default=10, help="Canary traffic weight (0-100)")
    parser.add_argument("--version", required=True, help="New image version/tag")
    args = parser.parse_args()

    port = SERVICE_PORTS[args.service]
    manifest = generate_canary(args.service, port, args.weight, args.version)

    output_path = os.path.join(
        os.path.dirname(__file__), "services", f"{args.service}-canary.yaml"
    )
    with open(output_path, "w") as f:
        f.write(manifest)
    print(f"✓ Canary manifest written: {output_path}")
    print(f"  Service: {args.service}")
    print(f"  Version: {args.version}")
    print(f"  Weight:  {args.weight}%")
    print(f"\nApply with: kubectl apply -f {output_path}")
