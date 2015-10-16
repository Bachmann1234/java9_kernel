from kernel import JavaKernel


if __name__ == '__main__':
    try:
        from ipykernel.kernelapp import IPKernelApp
    except:
        from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=JavaKernel)
