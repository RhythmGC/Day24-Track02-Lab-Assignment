# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [ ] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [ ] Backup cũng phải ở trong lãnh thổ VN
- [ ] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [ ] Thu thập consent trước khi dùng data cho AI training
- [ ] Có mechanism để user rút consent (Right to Erasure)
- [ ] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [ ] Có incident response plan
- [ ] Alert tự động khi phát hiện breach
- [ ] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [ ] Đã bổ nhiệm Data Protection Officer
- [ ] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | 🚧 In Progress | Infra Team |
| Audit logging | CloudTrail + API access logs | ✅ Done | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus) | ✅ Done | Security Team |

## F. Technical Solutions for Pending Items
**Audit logging (CloudTrail + API access logs):**
We will enable AWS CloudTrail to log all API calls across the infrastructure. For the FastAPI application, we will implement custom middleware to log every incoming request and its corresponding role/user ID, storing the logs securely in a centralized logging service like ELK or CloudWatch.

**Breach detection (Anomaly monitoring with Prometheus):**
We will configure Prometheus to monitor API error rates, unusual data access patterns (e.g. excessive downloads), and sudden spikes in traffic. Alerts will be set up via Alertmanager to notify the Security Team immediately through PagerDuty/Slack if an anomaly is detected.

- Audit logging: bật API gateway access logs, ghi log RBAC decisions, và đẩy audit trail vào hệ thống log tập trung (ELK/CloudWatch) với retention 12-24 tháng.
- Breach detection: thiết lập Prometheus alert rules cho truy cập bất thường (spike 4xx/5xx, access to raw PII), tích hợp Alertmanager gửi thông báo Slack/Email và runbook xử lý sự cố.
