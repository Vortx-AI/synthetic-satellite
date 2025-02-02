# Token Economics and Governance

## Overview
This document details the token economics and governance model of the Vortx Earth Memory System, focusing on the $VORTX token utility, distribution, and governance mechanisms.

## Token Economics

### Token Distribution Planned
```mermaid
pie title $VORTX Token Distribution
    "Ecosystem Rewards" : 10
    "Development" : 20
    "Foundation" : 15
    "Team" : 35
    "Investors" : 15
    "Community" : 5
```

### Token Specifications
```python
TOKEN_SPECS = {
    'token': {
        'name': 'Vortx',
        'symbol': '$VORTX',
        'type': 'Utility Token',
        'standard': 'ERC-20',
        'total_supply': '1,000,000,000',
        'decimal_places': 18
    },
    'distribution': {
        'ecosystem_rewards': {
            'percentage': '40%',
            'vesting': 'Linear over 4 years',
            'cliff': 'None',
            'allocation': {
                'data_providers': '15%',
                'compute_providers': '15%',
                'intelligence_providers': '10%'
            }
        },
        'development': {
            'percentage': '20%',
            'vesting': 'Linear over 5 years',
            'cliff': '1 year',
            'allocation': {
                'research': '10%',
                'development': '7%',
                'operations': '3%'
            }
        },
        'foundation': {
            'percentage': '15%',
            'vesting': 'Linear over 5 years',
            'cliff': 'None',
            'allocation': {
                'grants': '5%',
                'partnerships': '5%',
                'ecosystem_growth': '5%'
            }
        },
        'team': {
            'percentage': '15%',
            'vesting': 'Linear over 4 years',
            'cliff': '1 year',
            'allocation': {
                'founders': '5%',
                'core_team': '7%',
                'future_hires': '3%'
            }
        },
        'advisors': {
            'percentage': '5%',
            'vesting': 'Linear over 2 years',
            'cliff': '6 months'
        },
        'community': {
            'percentage': '5%',
            'vesting': 'None',
            'allocation': {
                'airdrops': '2%',
                'rewards': '3%'
            }
        }
    }
}
```

### Token Utility Model
```mermaid
graph TD
    subgraph Data Economy
        D1[Data Providers] -->|Stake & Earn| D2[Data Pool]
        D2 -->|Data Verification| D3[Quality Analysis]
        D3 -->|Performance Analysis| D4[Data Rewards]
    end
    
    subgraph Compute Economy
        C1[Compute Providers] -->|Stake & Process| C2[Compute Pool]
        C2 -->|Resource Verification| C3[Performance Analysis]
        C3 -->|Resource Analysis| C4[Compute Rewards]
    end
    
    subgraph Intelligence Economy
        I1[AGI Services] -->|Stake & Serve| I2[Intelligence Pool]
        I2 -->|Service Verification| I3[Value Analysis]
        I3 -->|Impact Analysis| I4[Intelligence Rewards]
    end
    
    subgraph Token Flow
        T1[$VORTX Token Pool] -->|Staking Allocation| T2[Provider Staking]
        T2 -->|Data Staking| D1
        T2 -->|Compute Staking| C1
        T2 -->|Intelligence Staking| I1
        
        D4 -->|Data Rewards| T3[Reward Distribution]
        C4 -->|Compute Rewards| T3
        I4 -->|Intelligence Rewards| T3
        
        T3 -->|Distribution| T1
    end
    
    classDef economy fill:#f9f,stroke:#333,stroke-width:2px
    classDef pool fill:#ff9,stroke:#333,stroke-width:2px
    classDef token fill:#9f9,stroke:#333,stroke-width:2px
    
    class D1,D2,D3,D4 economy
    class C1,C2,C3,C4 economy
    class I1,I2,I3,I4 economy
    class T1,T2,T3 token
```

### Reward Mechanisms
```python
REWARD_MECHANISMS = {
    'data_rewards': {
        'base_rate': {
            'amount': '100 VORTX/TB',
            'adjustment': 'Dynamic based on quality',
            'frequency': 'Per validation cycle'
        },
        'quality_multiplier': {
            'range': '1.0-3.0',
            'factors': {
                'accuracy': 0.4,
                'uniqueness': 0.3,
                'timeliness': 0.3
            }
        },
        'staking_requirements': {
            'minimum': '10000 VORTX',
            'optimal': '100000 VORTX',
            'maximum_boost': '3x'
        }
    },
    'compute_rewards': {
        'base_rate': {
            'amount': '1000 VORTX/PFLOP-hour',
            'adjustment': 'Dynamic based on demand',
            'frequency': 'Per computation cycle'
        },
        'performance_multiplier': {
            'range': '1.0-2.5',
            'factors': {
                'reliability': 0.4,
                'speed': 0.3,
                'efficiency': 0.3
            }
        },
        'staking_requirements': {
            'minimum': '50000 VORTX',
            'optimal': '500000 VORTX',
            'maximum_boost': '2.5x'
        }
    },
    'intelligence_rewards': {
        'base_rate': {
            'amount': '10000 VORTX/model/month',
            'adjustment': 'Dynamic based on usage',
            'frequency': 'Monthly'
        },
        'value_multiplier': {
            'range': '1.0-4.0',
            'factors': {
                'accuracy': 0.3,
                'uniqueness': 0.3,
                'utility': 0.4
            }
        },
        'staking_requirements': {
            'minimum': '100000 VORTX',
            'optimal': '1000000 VORTX',
            'maximum_boost': '4x'
        }
    }
}
```

## Governance Model

### Governance Architecture
```mermaid
graph TD
    subgraph Voting Power
        V1[$VORTX Staking] -->|Base Power| V2[Base Voting Power]
        V2 -->|Time Lock| V3[Enhanced Voting Power]
        V3 -->|Participation| V4[Final Voting Power]
    end
    
    subgraph Token Flow
        T1[$VORTX Token Pool] -->|Governance Staking| V1
        V4 -->|Voting Weight| T2[Governance Power]
        T2 -->|Proposal Creation| P1
        T2 -->|Voting Rights| P3
    end
    
    subgraph Proposal System
        P1[Community Proposals] -->|Submission| P2[Proposal Review]
        P2 -->|Discussion| P3[Governance Vote]
        P3 -->|Execution| P4[Implementation]
    end
    
    subgraph Execution Layer
        E1[Smart Contracts] -->|Parameter Updates| E2[Protocol Changes]
        E2 -->|Validation| E3[State Updates]
        E3 -->|Monitoring| E4[Performance Analysis]
    end
    
    P4 -->|Trigger| E1
    E4 -->|Feedback| P1
    
    classDef voting fill:#f9f,stroke:#333,stroke-width:2px
    classDef token fill:#ff9,stroke:#333,stroke-width:2px
    classDef proposal fill:#9f9,stroke:#333,stroke-width:2px
    classDef execution fill:#9f9,stroke:#333,stroke-width:2px
    
    class V1,V2,V3,V4 voting
    class T1,T2 token
    class P1,P2,P3,P4 proposal
    class E1,E2,E3,E4 execution
```

### Governance Parameters
```python
GOVERNANCE_PARAMS = {
    'voting_power': {
        'calculation': {
            'base': 'Staked Amount',
            'time_multiplier': {
                'range': '1.0-2.0',
                'max_lock': '4 years'
            },
            'participation_boost': {
                'range': '1.0-1.5',
                'factors': ['proposal_creation', 'voting_history']
            }
        },
        'delegation': {
            'enabled': True,
            'max_delegations': 10,
            'min_delegation': '1000 VORTX'
        }
    },
    'proposal_system': {
        'creation': {
            'threshold': '100000 VORTX',
            'fee': '1000 VORTX',
            'cool_down': '7 days'
        },
        'voting': {
            'duration': '14 days',
            'quorum': '40%',
            'majority': '66%'
        },
        'execution': {
            'timelock': '48 hours',
            'grace_period': '24 hours'
        }
    },
    'parameter_ranges': {
        'reward_rates': {
            'min_adjustment': '-20%',
            'max_adjustment': '+20%',
            'frequency': '30 days'
        },
        'staking_requirements': {
            'min_adjustment': '-10%',
            'max_adjustment': '+10%',
            'frequency': '90 days'
        },
        'governance_settings': {
            'min_adjustment': '-5%',
            'max_adjustment': '+5%',
            'frequency': '180 days'
        }
    }
}
```

## Economic Security

### Staking Mechanics
```mermaid
graph TD
    subgraph Staking Pools
        S1[$VORTX Data Staking] -->|Secures| D[Data Network]
        S2[$VORTX Compute Staking] -->|Secures| C[Compute Network]
        S3[$VORTX Intelligence Staking] -->|Secures| I[Intelligence Network]
    end
    
    subgraph Token Flow
        T1[$VORTX Token Pool] -->|Allocation| S1
        T1 -->|Allocation| S2
        T1 -->|Allocation| S3
        
        M1 -->|Quality Rewards| T2[Reward Pool]
        M2 -->|Performance Rewards| T2
        M3 -->|Value Rewards| T2
        
        T2 -->|Distribution| T1
    end
    
    subgraph Security Validation
        D -->|Validates| V1[Data Quality]
        C -->|Ensures| V2[Compute Integrity]
        I -->|Verifies| V3[Intelligence Value]
        
        V1 -->|Metrics| M1[Quality Score]
        V2 -->|Metrics| M2[Performance Score]
        V3 -->|Metrics| M3[Value Score]
    end
    
    subgraph Penalties
        M1 -->|Triggers| P1[Data Slashing]
        M2 -->|Triggers| P2[Compute Slashing]
        M3 -->|Triggers| P3[Intelligence Slashing]
        
        P1 -->|Updates| S1
        P2 -->|Updates| S2
        P3 -->|Updates| S3
    end
    
    classDef staking fill:#f9f,stroke:#333,stroke-width:2px
    classDef token fill:#ff9,stroke:#333,stroke-width:2px
    classDef validation fill:#9f9,stroke:#333,stroke-width:2px
    classDef penalty fill:#9f9,stroke:#333,stroke-width:2px
    
    class S1,S2,S3 staking
    class T1,T2 token
    class V1,V2,V3,M1,M2,M3 validation
    class P1,P2,P3 penalty
```

### Security Parameters
```python
SECURITY_PARAMS = {
    'slashing_conditions': {
        'data_network': {
            'invalid_data': {
                'threshold': '3 strikes',
                'penalty': '10% stake',
                'lockout': '30 days'
            },
            'manipulation': {
                'threshold': '1 strike',
                'penalty': '50% stake',
                'lockout': '180 days'
            }
        },
        'compute_network': {
            'downtime': {
                'threshold': '99% uptime',
                'penalty': '5% stake',
                'lockout': '7 days'
            },
            'malicious_behavior': {
                'threshold': '1 strike',
                'penalty': '100% stake',
                'lockout': '365 days'
            }
        },
        'intelligence_network': {
            'poor_performance': {
                'threshold': '3 strikes',
                'penalty': '20% stake',
                'lockout': '60 days'
            },
            'malicious_models': {
                'threshold': '1 strike',
                'penalty': '100% stake',
                'lockout': '365 days'
            }
        }
    }
}
```

## Implementation Notes

1. All token metrics and parameters are subject to governance
2. Security measures are designed to ensure network stability
3. Reward mechanisms are designed to incentivize quality
4. Governance parameters are optimized for decentralization

## References

1. Token Economic Models
2. Governance Best Practices
3. DeFi Security Standards
4. Staking Mechanism Designs

## Version History

- v2.0.0 (2024): Initial comprehensive documentation
- v2.1.0 (Planned): Enhanced governance mechanisms
- v2.2.0 (Planned): Advanced staking features
``` 
