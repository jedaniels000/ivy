# global
import random
from hypothesis import given, strategies as st


# local
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_cmd_line_args


@st.composite
def x_and_filters(draw, dim: int = 2, transpose: bool = False):
    if not isinstance(dim, int):
        dim = draw(dim)
    strides = draw(
        st.one_of(
            st.lists(st.integers(min_value=1, max_value=2), min_size=dim, max_size=dim),
            st.integers(min_value=1, max_value=2),
        )
    )
    padding = draw(
        st.one_of(
            st.sampled_from(["same", "valid"]) if strides == 1 else st.just("valid"),
            st.integers(min_value=1, max_value=3),
            st.lists(st.integers(min_value=1, max_value=2), min_size=dim, max_size=dim),
        )
    )
    batch_size = 1
    filter_shape = draw(
        helpers.get_shape(
            min_num_dims=dim, max_num_dims=dim, min_dim_size=1, max_dim_size=5
        )
    )
    dtype = draw(helpers.get_dtypes("float", full=False))
    input_channels = draw(st.integers(1, 3))
    output_channels = draw(st.integers(1, 3))
    group_list = [i for i in range(1, 3)]
    if not transpose:
        group_list = list(filter(lambda x: (input_channels % x == 0), group_list))
    else:
        group_list = list(filter(lambda x: (output_channels % x == 0), group_list))
    fc = draw(st.sampled_from(group_list))
    dilations = draw(st.integers(1, 3))

    x_dim = []
    if transpose:
        x_dim = draw(
            helpers.get_shape(
                min_num_dims=dim, max_num_dims=dim, min_dim_size=1, max_dim_size=5
            )
        )
    else:
        for i in range(dim):
            min_x = filter_shape[i] + (filter_shape[i] - 1) * (dilations - 1)
            x_dim.append(draw(st.integers(min_x, 15)))
        x_dim = tuple(x_dim)
    if not transpose:
        output_channels = output_channels * fc
        filter_shape = (output_channels, input_channels // fc) + filter_shape
    else:
        input_channels = input_channels * fc
        filter_shape = filter_shape + (input_channels, output_channels // fc)
    x_shape = (batch_size, input_channels) + x_dim
    vals = draw(
        helpers.array_values(
            dtype=dtype[0],
            shape=x_shape,
            min_value=0.0,
            max_value=1.0,
        )
    )
    filters = draw(
        helpers.array_values(
            dtype=dtype[0],
            shape=filter_shape,
            min_value=0.0,
            max_value=1.0,
        )
    )
    bias = draw(
        helpers.array_values(
            dtype=dtype[0],
            shape=(output_channels,),
            min_value=0.0,
            max_value=1.0,
        )
    )
    return dtype, vals, filters, bias, dilations, strides, padding, fc


@handle_cmd_line_args
@given(
    dtype_vals=x_and_filters(dim=1),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.torch.conv1d"
    ),
)
def test_torch_conv1d(
    dtype_vals,
    num_positional_args,
    as_variable,
    native_array,
):
    dtype, vals, weight, bias, dilations, strides, padding, fc = dtype_vals
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend="torch",
        fn_tree="conv1d",
        input=vals,
        weight=weight,
        bias=bias,
        stride=strides,
        padding=padding,
        dilation=dilations,
        groups=fc,
    )


@handle_cmd_line_args
@given(
    dtype_vals=x_and_filters(dim=2),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.torch.conv2d"
    ),
)
def test_torch_conv2d(
    dtype_vals,
    num_positional_args,
    as_variable,
    native_array,
):
    dtype, vals, weight, bias, dilations, strides, padding, fc = dtype_vals
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend="torch",
        fn_tree="conv2d",
        input=vals,
        weight=weight,
        bias=bias,
        stride=strides,
        padding=padding,
        dilation=dilations,
        groups=fc,
    )


@handle_cmd_line_args
@given(
    dtype_vals=x_and_filters(dim=3),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.torch.conv3d"
    ),
)
def test_torch_conv3d(
    dtype_vals,
    num_positional_args,
    as_variable,
    native_array,
):
    dtype, vals, weight, bias, dilations, strides, padding, fc = dtype_vals
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend="torch",
        fn_tree="conv3d",
        input=vals,
        weight=weight,
        bias=bias,
        stride=strides,
        padding=padding,
        dilation=dilations,
        groups=fc,
    )


@st.composite
def _int_or_tuple(draw, min_val, max_val):
    val = draw(
        random.choice(
            [
                st.integers(min_val, max_val),
                st.tuples(st.integers(min_val, max_val)),
                st.tuples(
                    st.integers(min_val, max_val),
                    st.integers(min_val, max_val),
                ),
            ]
        )
    )
    return val


@handle_cmd_line_args
@given(
    dtype_and_input_and_shape=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        shape=(1, 3, 6, 6),
    ),
    kernel_size=_int_or_tuple(2, 5),
    dilation=_int_or_tuple(1, 3),
    padding=_int_or_tuple(0, 2),
    stride=_int_or_tuple(1, 3),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.torch.nn.functional.unfold"
    ),
)
def test_torch_unfold(
    dtype_and_input_and_shape,
    kernel_size,
    dilation,
    padding,
    stride,
    as_variable,
    num_positional_args,
    native_array,
    fw,
):
    args_dtypes = list([dtype_and_input_and_shape[0]] + ["uint8"] * 4)
    helpers.test_frontend_function(
        input_dtypes=args_dtypes,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        fw=fw,
        frontend="torch",
        fn_tree="nn.functional.unfold",
        input=dtype_and_input_and_shape[1],
        kernel_size=kernel_size,
        dilation=dilation,
        padding=padding,
        stride=stride,
    )


@handle_cmd_line_args
@given(
    dtype_and_input_and_shape=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float"),
        shape=(1, 12, 12),
    ),
    output_size=_int_or_tuple(3, 5),
    kernel_size=_int_or_tuple(2, 5),
    dilation=_int_or_tuple(1, 3),
    padding=_int_or_tuple(0, 2),
    stride=_int_or_tuple(1, 3),
    num_positional_args=helpers.num_positional_args(
        fn_name="ivy.functional.frontends.torch.nn.functional.fold"
    ),
)
def test_torch_fold(
    dtype_and_input_and_shape,
    output_size,
    kernel_size,
    dilation,
    padding,
    stride,
    as_variable,
    num_positional_args,
    native_array,
    fw,
):
    args_dtypes = list([dtype_and_input_and_shape[0]] + ["uint8"] * 5)
    helpers.test_frontend_function(
        input_dtypes=args_dtypes,
        as_variable_flags=as_variable,
        with_out=False,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        fw=fw,
        frontend="torch",
        fn_tree="nn.functional.fold",
        input=dtype_and_input_and_shape[1],
        output_size=output_size,
        kernel_size=kernel_size,
        dilation=dilation,
        padding=padding,
        stride=stride,
    )
