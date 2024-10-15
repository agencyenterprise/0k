mod zerok_compiler;
use zerok_compiler::zerok_backend::executor;
extern crate serde as serde_crate;
use expander_compiler::frontend::internal::Serde;
use halo2curves::{bn256::Fr, ff::FromUniformBytes};
use serde_crate::Deserialize;
use serde_json;
#[derive(Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Expression {
    Operation {
        op: Operation,
        left: Box<Expression>,
        right: Box<Expression>,
    },
    Const {
        const_value: u32,
    },
    Var {
        var: u32,
    },
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "lowercase")]
enum Operation {
    Add,
    Mul,
}

use expander_compiler::frontend::*; // Import the Serde trait

fn deserialize_dag(builder: &mut API<BN254Config>, x: &[Variable], expr: &Expression) -> Variable {
    match expr {
        Expression::Operation { op, left, right } => {
            let left_var = deserialize_dag(builder, x, left);
            let right_var = deserialize_dag(builder, x, right);

            match op {
                Operation::Add => builder.add(left_var, right_var),
                Operation::Mul => builder.mul(left_var, right_var),
            }
        }
        Expression::Const { const_value } => {
            builder.constant(BN254::from(*const_value as u64)) // Add a constant
        }
        Expression::Var { var } => {
            x[*var as usize] // Reference the variable (e.g., x[0] or x[1])
        }
    }
}

declare_circuit!(Circuit {
    sum: PublicVariable,
    x: [Variable; 174],
});

impl Define<BN254Config> for Circuit<Variable> {
    fn define(&self, builder: &mut API<BN254Config>) {
        // Define the JSON input representing the DAG
        let json_dag = r#"
        {
    "operation": {
        "op": "add",
        "left": {
            "operation": {
                "op": "mul",
                "left": {
                    "operation": {
                        "op": "add",
                        "left": {
                            "operation": {
                                "op": "add",
                                "left": {
                                    "operation": {
                                        "op": "add",
                                        "left": {
                                            "operation": {
                                                "op": "add",
                                                "left": {
                                                    "operation": {
                                                        "op": "add",
                                                        "left": {
                                                            "operation": {
                                                                "op": "add",
                                                                "left": {
                                                                    "operation": {
                                                                        "op": "add",
                                                                        "left": {
                                                                            "operation": {
                                                                                "op": "add",
                                                                                "left": {
                                                                                    "operation": {
                                                                                        "op": "add",
                                                                                        "left": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "operation": {
                                                                                                        "op": "mul",
                                                                                                        "left": {
                                                                                                            "operation": {
                                                                                                                "op": "add",
                                                                                                                "left": {
                                                                                                                    "operation": {
                                                                                                                        "op": "mul",
                                                                                                                        "left": {
                                                                                                                            "operation": {
                                                                                                                                "op": "add",
                                                                                                                                "left": {
                                                                                                                                    "operation": {
                                                                                                                                        "op": "mul",
                                                                                                                                        "left": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 57
                                                                                                                                            }
                                                                                                                                        },
                                                                                                                                        "right": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 1
                                                                                                                                            }
                                                                                                                                        }
                                                                                                                                    }
                                                                                                                                },
                                                                                                                                "right": {
                                                                                                                                    "operation": {
                                                                                                                                        "op": "mul",
                                                                                                                                        "left": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 58
                                                                                                                                            }
                                                                                                                                        },
                                                                                                                                        "right": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 2
                                                                                                                                            }
                                                                                                                                        }
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "const": {
                                                                                                                                "const_value": 100
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "operation": {
                                                                                                                        "op": "mul",
                                                                                                                        "left": {
                                                                                                                            "var": {
                                                                                                                                "var": 22
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "const": {
                                                                                                                                "const_value": 100
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "const": {
                                                                                                                "const_value": 10
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "var": {
                                                                                                        "var": 33
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "operation": {
                                                                                                        "op": "mul",
                                                                                                        "left": {
                                                                                                            "operation": {
                                                                                                                "op": "add",
                                                                                                                "left": {
                                                                                                                    "operation": {
                                                                                                                        "op": "mul",
                                                                                                                        "left": {
                                                                                                                            "operation": {
                                                                                                                                "op": "add",
                                                                                                                                "left": {
                                                                                                                                    "operation": {
                                                                                                                                        "op": "mul",
                                                                                                                                        "left": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 57
                                                                                                                                            }
                                                                                                                                        },
                                                                                                                                        "right": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 3
                                                                                                                                            }
                                                                                                                                        }
                                                                                                                                    }
                                                                                                                                },
                                                                                                                                "right": {
                                                                                                                                    "operation": {
                                                                                                                                        "op": "mul",
                                                                                                                                        "left": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 58
                                                                                                                                            }
                                                                                                                                        },
                                                                                                                                        "right": {
                                                                                                                                            "var": {
                                                                                                                                                "var": 4
                                                                                                                                            }
                                                                                                                                        }
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "const": {
                                                                                                                                "const_value": 100
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "operation": {
                                                                                                                        "op": "mul",
                                                                                                                        "left": {
                                                                                                                            "var": {
                                                                                                                                "var": 23
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "const": {
                                                                                                                                "const_value": 100
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "const": {
                                                                                                                "const_value": 10
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "var": {
                                                                                                        "var": 34
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "operation": {
                                                                                        "op": "mul",
                                                                                        "left": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "operation": {
                                                                                                        "op": "add",
                                                                                                        "left": {
                                                                                                            "operation": {
                                                                                                                "op": "mul",
                                                                                                                "left": {
                                                                                                                    "operation": {
                                                                                                                        "op": "add",
                                                                                                                        "left": {
                                                                                                                            "operation": {
                                                                                                                                "op": "mul",
                                                                                                                                "left": {
                                                                                                                                    "var": {
                                                                                                                                        "var": 57
                                                                                                                                    }
                                                                                                                                },
                                                                                                                                "right": {
                                                                                                                                    "var": {
                                                                                                                                        "var": 5
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "operation": {
                                                                                                                                "op": "mul",
                                                                                                                                "left": {
                                                                                                                                    "var": {
                                                                                                                                        "var": 58
                                                                                                                                    }
                                                                                                                                },
                                                                                                                                "right": {
                                                                                                                                    "var": {
                                                                                                                                        "var": 6
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "const": {
                                                                                                                        "const_value": 100
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "operation": {
                                                                                                                "op": "mul",
                                                                                                                "left": {
                                                                                                                    "var": {
                                                                                                                        "var": 24
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "const": {
                                                                                                                        "const_value": 100
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "const": {
                                                                                                        "const_value": 10
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "var": {
                                                                                                "var": 35
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "operation": {
                                                                                "op": "mul",
                                                                                "left": {
                                                                                    "operation": {
                                                                                        "op": "mul",
                                                                                        "left": {
                                                                                            "operation": {
                                                                                                "op": "add",
                                                                                                "left": {
                                                                                                    "operation": {
                                                                                                        "op": "mul",
                                                                                                        "left": {
                                                                                                            "operation": {
                                                                                                                "op": "add",
                                                                                                                "left": {
                                                                                                                    "operation": {
                                                                                                                        "op": "mul",
                                                                                                                        "left": {
                                                                                                                            "var": {
                                                                                                                                "var": 57
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "var": {
                                                                                                                                "var": 7
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "operation": {
                                                                                                                        "op": "mul",
                                                                                                                        "left": {
                                                                                                                            "var": {
                                                                                                                                "var": 58
                                                                                                                            }
                                                                                                                        },
                                                                                                                        "right": {
                                                                                                                            "var": {
                                                                                                                                "var": 8
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "const": {
                                                                                                                "const_value": 100
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "operation": {
                                                                                                        "op": "mul",
                                                                                                        "left": {
                                                                                                            "var": {
                                                                                                                "var": 25
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "const": {
                                                                                                                "const_value": 100
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "const": {
                                                                                                "const_value": 10
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "var": {
                                                                                        "var": 36
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "right": {
                                                                    "operation": {
                                                                        "op": "mul",
                                                                        "left": {
                                                                            "operation": {
                                                                                "op": "mul",
                                                                                "left": {
                                                                                    "operation": {
                                                                                        "op": "add",
                                                                                        "left": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "operation": {
                                                                                                        "op": "add",
                                                                                                        "left": {
                                                                                                            "operation": {
                                                                                                                "op": "mul",
                                                                                                                "left": {
                                                                                                                    "var": {
                                                                                                                        "var": 57
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "var": {
                                                                                                                        "var": 9
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "operation": {
                                                                                                                "op": "mul",
                                                                                                                "left": {
                                                                                                                    "var": {
                                                                                                                        "var": 58
                                                                                                                    }
                                                                                                                },
                                                                                                                "right": {
                                                                                                                    "var": {
                                                                                                                        "var": 10
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "const": {
                                                                                                        "const_value": 100
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "var": {
                                                                                                        "var": 26
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "const": {
                                                                                                        "const_value": 100
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "const": {
                                                                                        "const_value": 10
                                                                                    }
                                                                                }
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "var": {
                                                                                "var": 37
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "right": {
                                                            "operation": {
                                                                "op": "mul",
                                                                "left": {
                                                                    "operation": {
                                                                        "op": "mul",
                                                                        "left": {
                                                                            "operation": {
                                                                                "op": "add",
                                                                                "left": {
                                                                                    "operation": {
                                                                                        "op": "mul",
                                                                                        "left": {
                                                                                            "operation": {
                                                                                                "op": "add",
                                                                                                "left": {
                                                                                                    "operation": {
                                                                                                        "op": "mul",
                                                                                                        "left": {
                                                                                                            "var": {
                                                                                                                "var": 57
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "var": {
                                                                                                                "var": 11
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "operation": {
                                                                                                        "op": "mul",
                                                                                                        "left": {
                                                                                                            "var": {
                                                                                                                "var": 58
                                                                                                            }
                                                                                                        },
                                                                                                        "right": {
                                                                                                            "var": {
                                                                                                                "var": 12
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "const": {
                                                                                                "const_value": 100
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "operation": {
                                                                                        "op": "mul",
                                                                                        "left": {
                                                                                            "var": {
                                                                                                "var": 27
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "const": {
                                                                                                "const_value": 100
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "const": {
                                                                                "const_value": 10
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "right": {
                                                                    "var": {
                                                                        "var": 38
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                },
                                                "right": {
                                                    "operation": {
                                                        "op": "mul",
                                                        "left": {
                                                            "operation": {
                                                                "op": "mul",
                                                                "left": {
                                                                    "operation": {
                                                                        "op": "add",
                                                                        "left": {
                                                                            "operation": {
                                                                                "op": "mul",
                                                                                "left": {
                                                                                    "operation": {
                                                                                        "op": "add",
                                                                                        "left": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "var": {
                                                                                                        "var": 57
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "var": {
                                                                                                        "var": 13
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "operation": {
                                                                                                "op": "mul",
                                                                                                "left": {
                                                                                                    "var": {
                                                                                                        "var": 58
                                                                                                    }
                                                                                                },
                                                                                                "right": {
                                                                                                    "var": {
                                                                                                        "var": 14
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "const": {
                                                                                        "const_value": 100
                                                                                    }
                                                                                }
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "operation": {
                                                                                "op": "mul",
                                                                                "left": {
                                                                                    "var": {
                                                                                        "var": 28
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "const": {
                                                                                        "const_value": 100
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "right": {
                                                                    "const": {
                                                                        "const_value": 10
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "right": {
                                                            "var": {
                                                                "var": 39
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "right": {
                                            "operation": {
                                                "op": "mul",
                                                "left": {
                                                    "operation": {
                                                        "op": "mul",
                                                        "left": {
                                                            "operation": {
                                                                "op": "add",
                                                                "left": {
                                                                    "operation": {
                                                                        "op": "mul",
                                                                        "left": {
                                                                            "operation": {
                                                                                "op": "add",
                                                                                "left": {
                                                                                    "operation": {
                                                                                        "op": "mul",
                                                                                        "left": {
                                                                                            "var": {
                                                                                                "var": 57
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "var": {
                                                                                                "var": 15
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "operation": {
                                                                                        "op": "mul",
                                                                                        "left": {
                                                                                            "var": {
                                                                                                "var": 58
                                                                                            }
                                                                                        },
                                                                                        "right": {
                                                                                            "var": {
                                                                                                "var": 16
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "const": {
                                                                                "const_value": 100
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "right": {
                                                                    "operation": {
                                                                        "op": "mul",
                                                                        "left": {
                                                                            "var": {
                                                                                "var": 29
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "const": {
                                                                                "const_value": 100
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "right": {
                                                            "const": {
                                                                "const_value": 10
                                                            }
                                                        }
                                                    }
                                                },
                                                "right": {
                                                    "var": {
                                                        "var": 40
                                                    }
                                                }
                                            }
                                        }
                                    }
                                },
                                "right": {
                                    "operation": {
                                        "op": "mul",
                                        "left": {
                                            "operation": {
                                                "op": "mul",
                                                "left": {
                                                    "operation": {
                                                        "op": "add",
                                                        "left": {
                                                            "operation": {
                                                                "op": "mul",
                                                                "left": {
                                                                    "operation": {
                                                                        "op": "add",
                                                                        "left": {
                                                                            "operation": {
                                                                                "op": "mul",
                                                                                "left": {
                                                                                    "var": {
                                                                                        "var": 57
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "var": {
                                                                                        "var": 17
                                                                                    }
                                                                                }
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "operation": {
                                                                                "op": "mul",
                                                                                "left": {
                                                                                    "var": {
                                                                                        "var": 58
                                                                                    }
                                                                                },
                                                                                "right": {
                                                                                    "var": {
                                                                                        "var": 18
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "right": {
                                                                    "const": {
                                                                        "const_value": 100
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "right": {
                                                            "operation": {
                                                                "op": "mul",
                                                                "left": {
                                                                    "var": {
                                                                        "var": 30
                                                                    }
                                                                },
                                                                "right": {
                                                                    "const": {
                                                                        "const_value": 100
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                },
                                                "right": {
                                                    "const": {
                                                        "const_value": 10
                                                    }
                                                }
                                            }
                                        },
                                        "right": {
                                            "var": {
                                                "var": 41
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "right": {
                            "operation": {
                                "op": "mul",
                                "left": {
                                    "operation": {
                                        "op": "mul",
                                        "left": {
                                            "operation": {
                                                "op": "add",
                                                "left": {
                                                    "operation": {
                                                        "op": "mul",
                                                        "left": {
                                                            "operation": {
                                                                "op": "add",
                                                                "left": {
                                                                    "operation": {
                                                                        "op": "mul",
                                                                        "left": {
                                                                            "var": {
                                                                                "var": 57
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "var": {
                                                                                "var": 19
                                                                            }
                                                                        }
                                                                    }
                                                                },
                                                                "right": {
                                                                    "operation": {
                                                                        "op": "mul",
                                                                        "left": {
                                                                            "var": {
                                                                                "var": 58
                                                                            }
                                                                        },
                                                                        "right": {
                                                                            "var": {
                                                                                "var": 20
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        },
                                                        "right": {
                                                            "const": {
                                                                "const_value": 100
                                                            }
                                                        }
                                                    }
                                                },
                                                "right": {
                                                    "operation": {
                                                        "op": "mul",
                                                        "left": {
                                                            "var": {
                                                                "var": 31
                                                            }
                                                        },
                                                        "right": {
                                                            "const": {
                                                                "const_value": 100
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        "right": {
                                            "const": {
                                                "const_value": 10
                                            }
                                        }
                                    }
                                },
                                "right": {
                                    "var": {
                                        "var": 42
                                    }
                                }
                            }
                        }
                    }
                },
                "right": {
                    "const": {
                        "const_value": 100
                    }
                }
            }
        },
        "right": {
            "operation": {
                "op": "mul",
                "left": {
                    "var": {
                        "var": 54
                    }
                },
                "right": {
                    "const": {
                        "const_value": 100
                    }
                }
            }
        }
    }
}
        "#;
        let parsed_dag: Expression = match serde_json::from_str(json_dag) {
            Ok(dag) => {
                println!("Parsed DAG: {:?}", dag);
                dag
            }
            Err(e) => panic!("Failed to parse JSON DAG: {}", e),
        };
        // Use the deserialized DAG to build the circuit
        let sum = deserialize_dag(builder, &self.x, &parsed_dag);

        // Assert that the computed sum equals the expected public value
        builder.assert_is_equal(sum, self.sum);
    }
}

fn bigint_to_fr(u256_value: &str) -> Fr {
    // Convert the U256 to a BigUint (num-bigint's large number representation)
    let large_number = num_bigint::BigUint::parse_bytes(u256_value.as_bytes(), 10).unwrap();

    // Initialize a 64-byte array
    let mut bytes = [0u8; 64];

    // Convert the BigUint into a byte array in little-endian order
    let large_bytes = large_number.to_bytes_le();

    // Copy the bytes into the 64-byte array
    bytes[..large_bytes.len()].copy_from_slice(&large_bytes);

    // Call the `from_uniform_bytes` function to convert the bytes into Fr
    Fr::from_uniform_bytes(&bytes)
}
fn main() {
    let compile_result = compile(&Circuit::default()).unwrap();
    let assignment = Circuit::<BN254> {
        sum: BN254::from(bigint_to_fr(
            "21888242871839275222246405745257275088548364400416034343698204186575376896617",
        )),
        x: [
            BN254::from(bigint_to_fr("3")),
            BN254::from(bigint_to_fr("3")),
            BN254::from(bigint_to_fr("7")),
            BN254::from(bigint_to_fr("4")),
            BN254::from(bigint_to_fr("13")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495616",
            )),
            BN254::from(bigint_to_fr("3")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495612",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495612",
            )),
            BN254::from(bigint_to_fr("4")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495615",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495616",
            )),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr("6")),
            BN254::from(bigint_to_fr("1")),
            BN254::from(bigint_to_fr("6")),
            BN254::from(bigint_to_fr("5")),
            BN254::from(bigint_to_fr("5")),
            BN254::from(bigint_to_fr("12")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495612",
            )),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495613",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495612",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495616",
            )),
            BN254::from(bigint_to_fr("6")),
            BN254::from(bigint_to_fr("7")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495613",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495613",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495611",
            )),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr("2")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495616",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495613",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495610",
            )),
            BN254::from(bigint_to_fr("8")),
            BN254::from(bigint_to_fr("1")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495615",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("9")),
            BN254::from(bigint_to_fr("5")),
            BN254::from(bigint_to_fr("10")),
            BN254::from(bigint_to_fr("10")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495609",
            )),
            BN254::from(bigint_to_fr("10")),
            BN254::from(bigint_to_fr("10")),
            BN254::from(bigint_to_fr("20")),
            BN254::from(bigint_to_fr("30")),
            BN254::from(bigint_to_fr("140")),
            BN254::from(bigint_to_fr("170")),
            BN254::from(bigint_to_fr("40")),
            BN254::from(bigint_to_fr("260")),
            BN254::from(bigint_to_fr("300")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495607",
            )),
            BN254::from(bigint_to_fr("60")),
            BN254::from(bigint_to_fr("50")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495567",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495517",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495467",
            )),
            BN254::from(bigint_to_fr("40")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("40")),
            BN254::from(bigint_to_fr("20")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495577",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495597",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("20")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495597",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("20")),
            BN254::from(bigint_to_fr("120")),
            BN254::from(bigint_to_fr("140")),
            BN254::from(bigint_to_fr("10")),
            BN254::from(bigint_to_fr("120")),
            BN254::from(bigint_to_fr("130")),
            BN254::from(bigint_to_fr("17000")),
            BN254::from(bigint_to_fr("30000")),
            BN254::from(bigint_to_fr("5000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808480617",
            )),
            BN254::from(bigint_to_fr("4000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808493617",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("14000")),
            BN254::from(bigint_to_fr("13000")),
            BN254::from(bigint_to_fr("500")),
            BN254::from(bigint_to_fr("1200")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495117",
            )),
            BN254::from(bigint_to_fr("200")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495217",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495117",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495517",
            )),
            BN254::from(bigint_to_fr("600")),
            BN254::from(bigint_to_fr("700")),
            BN254::from(bigint_to_fr("17500")),
            BN254::from(bigint_to_fr("31200")),
            BN254::from(bigint_to_fr("4500")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808480817",
            )),
            BN254::from(bigint_to_fr("4000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808493217",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495117",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808495517",
            )),
            BN254::from(bigint_to_fr("14600")),
            BN254::from(bigint_to_fr("13700")),
            BN254::from(bigint_to_fr("175000")),
            BN254::from(bigint_to_fr("175000")),
            BN254::from(bigint_to_fr("312000")),
            BN254::from(bigint_to_fr("45000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808347617",
            )),
            BN254::from(bigint_to_fr("40000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808471617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808490617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808494617",
            )),
            BN254::from(bigint_to_fr("146000")),
            BN254::from(bigint_to_fr("137000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575807795617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575806623617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805923617",
            )),
            BN254::from(bigint_to_fr("90000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575806013617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808199617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805717617",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805717617",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805717617",
            )),
            BN254::from(bigint_to_fr("5000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805722617",
            )),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805722617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575807911617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575805138617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575807536617",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575804179617",
            )),
            BN254::from(bigint_to_fr("1400000")),
            BN254::from(bigint_to_fr("312000")),
            BN254::from(bigint_to_fr("1712000")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("1712000")),
            BN254::from(bigint_to_fr("296000")),
            BN254::from(bigint_to_fr("2008000")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("2008000")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("2008000")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("2008000")),
            BN254::from(bigint_to_fr("0")),
            BN254::from(bigint_to_fr("2008000")),
            BN254::from(bigint_to_fr("1314000")),
            BN254::from(bigint_to_fr("3322000")),
            BN254::from(bigint_to_fr("685000")),
            BN254::from(bigint_to_fr("4007000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575376895617",
            )),
            BN254::from(bigint_to_fr("400700000")),
            BN254::from(bigint_to_fr("1000")),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575808494817",
            )),
            BN254::from(bigint_to_fr(
                "21888242871839275222246405745257275088548364400416034343698204186575376896617",
            )),
            BN254::from(bigint_to_fr("400699200")),
        ],
    };

    let witness = compile_result
        .witness_solver
        .solve_witness(&assignment)
        .unwrap();
    let output = compile_result.layered_circuit.run(&witness);
    print!("OUTPUT: {:?}", output);
    assert_eq!(output, vec![true]);

    let file = std::fs::File::create("circuit.txt").unwrap();
    let writer = std::io::BufWriter::new(file);
    compile_result
        .layered_circuit
        .serialize_into(writer)
        .unwrap();

    let file = std::fs::File::create("witness.txt").unwrap();
    let writer = std::io::BufWriter::new(file);
    witness.serialize_into(writer).unwrap();

    let file = std::fs::File::create("witness_solver.txt").unwrap();
    let writer = std::io::BufWriter::new(file);
    compile_result
        .witness_solver
        .serialize_into(writer)
        .unwrap();
    executor();
}
