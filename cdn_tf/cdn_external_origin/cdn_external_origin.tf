resource "google_compute_global_forwarding_rule" "default" {
  name       = "test-cdn-fwd-rule"
  target     = google_compute_target_http_proxy.default.id
  port_range = "80"
}

resource "google_compute_target_http_proxy" "default" {
  name    = "test-proxy"
  url_map = google_compute_url_map.default.id
}

resource "google_compute_url_map" "default" {
  name            = "test-lb"
  default_service = google_compute_backend_service.default.id
}

resource "google_compute_global_network_endpoint_group" "external_proxy" {
  provider=google-beta
  name                  = "test-network-endpoint"
  network_endpoint_type = "INTERNET_FQDN_PORT"
  default_port          = "443"
}

resource "google_compute_global_network_endpoint" "proxy" {
  provider=google-beta
  global_network_endpoint_group = google_compute_global_network_endpoint_group.external_proxy.id
  fqdn                          = "object_storage.fqdn.com"
  port                          = google_compute_global_network_endpoint_group.external_proxy.default_port
}

resource "google_compute_backend_service" "default" {
  provider=google-beta
  name                            = "test-backend-service"
  enable_cdn                      = true
  timeout_sec                     = 10
  connection_draining_timeout_sec = 10

  custom_request_headers          = ["host: ${google_compute_global_network_endpoint.proxy.fqdn}"]
  custom_response_headers         = ["X-Cache-Hit: {cdn_cache_status}"]

  backend {
    group = google_compute_global_network_endpoint_group.external_proxy.id
  }
}