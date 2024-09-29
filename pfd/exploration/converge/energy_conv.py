from .check_conv import CheckConv


class EnerConvRMSE(CheckConv):
    def check_conv(self, test_res_ls, conv_config: dict):
        numb_frame = []
        rmse_e = []
        for res in test_res_ls:
            numb_frame.append(res["numb_frame"])
            rmse_e.append(res["RMSE_energy_per_at"])
        conv_rmse = conv_config["RMSE"]
        weighted_rmse = sum(n * rmse for n, rmse in zip(numb_frame, rmse_e)) / sum(
            numb_frame
        )
        converged = False
        if weighted_rmse < conv_rmse:
            converged = True
        return converged