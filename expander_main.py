import json
import onnx
import onnxruntime
import os
from zerok.ops.onnx_utils import generate_small_iris_onnx_model
from zerok.ops.from_onnx import from_onnx

# Define the prime number and scale factor
PRIME_MOD = (
    21888242871839275222246405745257275088548364400416034343698204186575808495617
)
SCALE_FACTOR = 10**1

# Global list to store variable values
dag_variable_list = []


class Value:
    def __init__(self, value, is_constant=False, convert_to_fixed=True, _op=None):
        if convert_to_fixed and _op is None:
            # Scale the number by 10^8 and take the modulus with the prime
            self.value = int(value * SCALE_FACTOR) % PRIME_MOD
        else:
            print(f"Value: {value} op: {_op}")
            self.value = value
        self.op = _op
        self.data = self.value
        if is_constant:
            self.is_constant = True
            # Scale the number by 10^8 and take the modulus with the prime
            self.index = None  # No index for constants
        else:
            self.is_constant = is_constant
            self.index = len(
                dag_variable_list
            )  # Assign the index based on the global list
            dag_variable_list.append(self.value)  # Add value to the global list

            print(f"Variable {self.value} created")
            self.value = self.index  # Use the index as the value for variables
            print(f"Variable {self.index} created")

        self.children = []

    def __add__(self, other):
        # Automatically convert int/float to Value with scaling and modulus
        if isinstance(other, (int, float)):
            other = Value((int(other * SCALE_FACTOR) % PRIME_MOD), is_constant=True)
        elif not isinstance(other, Value):
            raise TypeError("Unsupported type for addition")

        # Perform addition (mod PRIME_MOD)
        result = (self.data + other.data) % PRIME_MOD
        new_node = Value(
            result, is_constant=self.is_constant and other.is_constant, _op="add"
        )

        # Track children (left: self, right: other)
        new_node.children = [self, other]

        return new_node

    def __mul__(self, other):
        # Automatically convert int/float to Value with scaling and modulus
        if isinstance(other, (int, float)):
            other = Value((int(other * SCALE_FACTOR) % PRIME_MOD), is_constant=True)
        elif not isinstance(other, Value):
            raise TypeError("Unsupported type for multiplication")

        # Perform multiplication (mod PRIME_MOD)
        result = (self.data * other.data) % PRIME_MOD
        new_node = Value(
            result, is_constant=self.is_constant and other.is_constant, _op="mul"
        )

        # Track children (left: self, right: other)
        new_node.children = [self, other]

        return new_node

    def relu(self):
        if self.data > 0:
            return self * Value(1, is_constant=True)
        else:
            return Value(0, is_constant=True) * self

    def serialize(self):
        # Leaf node: Variable or Constant
        if not self.children:
            if self.is_constant:
                return {"const": {"const_value": self.value}}
            else:
                return {"var": {"var": self.value}}  # Use index for variables

        # Otherwise, it's an operation node
        return {
            "operation": {
                "op": self.op,  # This will be "add" or "mul"
                "left": self.children[0].serialize(),
                "right": self.children[1].serialize(),
            }
        }

    def to_json(self):
        return json.dumps(self.serialize(), indent=4)

    def circuit_list(self):
        for var in dag_variable_list:
            print(f"Variable: {var}")


def add_intermediate_layers_as_outputs(onnx_model):
    """takes an onnx model and returns the same model but will all intermediate
    node outputs as outputs to the model.

    Useful for testing that all nodes are calculated correctly
    """

    shape_info = onnx.shape_inference.infer_shapes(onnx_model)

    value_info_protos = []
    for node in shape_info.graph.value_info:
        value_info_protos.append(node)

    onnx_model.graph.output.extend(value_info_protos)

    onnx.checker.check_model(onnx_model)

    return onnx_model


# if "iris_model.onnx" not in os.listdir("tests/assets/"):
#     generate_small_iris_onnx_model(onnx_output_path="tests/assets/iris_model.onnx")

# onnx_model = add_intermediate_layers_as_outputs(
#     onnx.load("tests/assets/iris_model.onnx")
# )

# # Create a dummy input
# dummy_input = [[1, 2]]  # np.random.randn(1, 2).astype(np.float32)

# # Run the model through onnx inference session
# session = onnxruntime.InferenceSession(onnx_model.SerializeToString())
# input_name = session.get_inputs()[0].name
# onnx_outputs = session.run(None, {input_name: dummy_input})
# assert len(onnx_outputs) == len(onnx_model.graph.output)
# zerok_outputs = from_onnx(onnx_model, dummy_input, base_class=Value)


# dag = zerok_outputs[0][0][0]
# print(dag.to_json())
# with open("a.json", "w") as f:
#     d = {
#         "dag": json.loads(zerok_outputs[0][0][0].to_json()),
#         "witness": [str(x) for x in dag_variable_list],
#     }
#     f.write(json.dumps(d))
# print(dag.data)
dag = Value(1) * Value(2)
print(dag.to_json())

from zerok_template import create_zerok_compiler_file_content, execute_zerok_compiler


def build_compiler_file(
    dag: Value, num_variables: int, output: int, witness: list[int]
):
    with open("zerok.rs", "+w") as f:
        f.write(
            create_zerok_compiler_file_content(
                dag=dag.to_json(),
                num_variables=len(witness),
                output=dag.data,
                witness=witness,
            )
        )


if __name__ == "__main__":
    build_compiler_file(dag, len(dag_variable_list), dag.data, dag_variable_list)
    print("Compiler file generated")
    print("Executing the compiler")
    execute_zerok_compiler()
    print("Done")
