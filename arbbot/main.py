from arbbot.opp_checker import main_async

import csv




def save_logs(self, row_content):
    # Move this function to helpers
    # + create listeners
    with open(self.save_logs_path, "a") as stats_file:
        writer = csv.DictWriter(stats_file, fieldnames=row_content.keys())
        # writer.writeheader()
        writer.writerow(row_content)


