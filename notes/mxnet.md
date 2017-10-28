Source code modification:
(1) change bigarray_bound_ from 1000*1000 to 10*1000 for more balanced workload on parameter servers. Specifically, set env variable MXNET_KVSTORE_BIGARRAY_BOUND.


#key ranges are evenly sliced and distributed to parameter servers

const std::vector<Range>& Postoffice::GetServerKeyRanges() {
  if (server_key_ranges_.empty()) {
    for (int i = 0; i < num_servers_; ++i) {
      server_key_ranges_.push_back(Range(
          kMaxKey / num_servers_ * i,
          kMaxKey / num_servers_ * (i+1)));
    }
  }
  return server_key_ranges_;
}


# keys are the addresses of parameter arrays. Each parameter array is formed for an argument in symbol.list_arguments()
def _update_params_on_kvstore(param_arrays, grad_arrays, kvstore):
    """Perform update of param_arrays from grad_arrays on kvstore."""
    for index, pair in enumerate(zip(param_arrays, grad_arrays)):
        arg_list, grad_list = pair
        if grad_list[0] is None:
            continue
        # push gradient, priority is negative index
        kvstore.push(index, grad_list, priority=-index)
        # pull back the weights
        kvstore.pull(index, arg_list, priority=-index)

  