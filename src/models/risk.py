class Risk:
    def __init__(self, device_id, risk_score=0, vulnerabilities=None, ports=None):
        self.device_id = device_id
        self.risk_score = risk_score
        self.vulnerabilities = vulnerabilities or []
        self.ports = ports or []

    def calculate_risk_score(self):
        # Enhanced risk calculation
        base_score = 0
        weights = {"critical": 10, "high": 5, "medium": 3, "low": 1}
        
        # Add score for vulnerabilities
        for vulnerability in self.vulnerabilities:
            severity = vulnerability.get('severity', 'low')
            base_score += weights.get(severity, 0)
        
        # Add score for open ports (certain ports increase risk)
        high_risk_ports = [23, 21, 22, 8080, 2323]
        for port in self.ports:
            if port in high_risk_ports:
                base_score += 3
                
        # Normalize to 0-100 scale
        self.risk_score = min(base_score * 5, 100)
        return self.risk_score
        
    def __repr__(self):
        return {
            "device_id": self.device_id,
            "risk_score": self.risk_score,
            "vulnerability_count": len(self.vulnerabilities),
            "port_count": len(self.ports)
        }