import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
from matplotlib import patches

# Step and time data from log (steps 1 to 75)
steps = np.arange(1, 76)
times = [22667.7, 12826.5, 10843.2, 10827.6, 10883.9, 11462.3, 10893.1, 12037.1, 10855.8, 10801.5,
         10837.8, 10802.6, 10794.2, 10811.4, 10836.0, 10808.0, 10841.8, 10839.4, 11528.8, 11572.4,
         10783.9, 10799.1, 10960.4, 10834.1, 10796.4, 10795.7, 10791.4, 11251.6, 10811.5, 10800.8,
         10812.1, 10816.9, 12487.5, 10838.9, 10774.2, 10821.1, 10996.8, 10817.5, 11070.1, 11082.7,
         10794.3, 10807.4, 10791.9, 10828.3, 11060.4, 10798.7, 11462.6, 10852.3, 10825.9, 10886.5,
         11096.5, 10802.5, 10819.6, 10816.5, 10793.1, 11083.4, 10802.5, 10808.4, 10813.6, 10844.2,
         11120.5, 10805.2, 10804.0, 10809.8, 10805.1, 10834.0, 11026.4, 10827.1, 10827.3, 10823.3,
         10799.5, 11067.1, 10826.7, 10862.1, 10838.5]

# After step 75, fall back to step 50, then 45 more steps (10 original + 16 new + 19 additional)
fallback_step = 50
extra_times = [10808.5, 11154.9, 11106.7, 10826.2, 10844.0, 10806.2, 10800.3, 11079.9, 10813.5, 10826.2,
               11298.1, 11251.8, 11297.6, 11305.1, 11365.9, 11318.3, 11314.0, 11303.2, 11312.2, 11293.0, 11298.7, 11296.2, 11307.4, 11300.9, 11298.0, 11303.4,10821.1, 10996.8, 10817.5, 11070.1, 11082.7,
               10698.0, 10692.1, 10702.2, 10842.6, 12261.4, 10771.9, 10768.4, 10782.4, 10769.4, 10763.0, 10752.3, 10750.1, 10764.8, 10763.2, 10837.1, 10749.3, 10754.9, 10924.6, 11226.9]

# Convert times from milliseconds to seconds
times_seconds = [t/1000 for t in times]
extra_times_seconds = [t/1000 for t in extra_times]

# Convert times from seconds to minutes
times_minutes = [t/60 for t in times_seconds]
extra_times_minutes = [t/60 for t in extra_times_seconds]

# Cumulative time up to step 75 (in minutes)
cum_times = np.cumsum(times_minutes)

# Build the main curve: steps 1-75
main_times = cum_times
main_steps = steps

# At step 75, fall back to step 50 (vertical drop at the same time)
fall_time = cum_times[-1]
fall_steps = [75, 50]
fall_times = [fall_time, fall_time]

# Add timeout (4min30s = 4.5min), scheduling (935s = 15.58min), and reboot (67s = 1.12min) after fallback
timeout_duration = 4.5  # 4 minutes 30 seconds
scheduling_duration = 15.58  # 935 seconds
reboot_duration = 2.5  # 2.5 minutes
total_delay = timeout_duration + scheduling_duration + reboot_duration

timeout_end = fall_time + timeout_duration
scheduling_end = timeout_end + scheduling_duration
delay_time = fall_time + total_delay

# Then continue with all extra steps and times, starting from delay_time
extra_cum_times = np.cumsum(extra_times_minutes) + delay_time
extra_curve_steps = np.arange(fallback_step+1, fallback_step+1+len(extra_times))  # Steps 51-95
extra_curve_times = extra_cum_times

# Comparison: continuous training without fallback (all steps 1-120)
all_times = times + extra_times
all_times_minutes = [t/60/1000 for t in all_times]  # Convert all to minutes
all_cum_times = np.cumsum(all_times_minutes)
all_steps = np.arange(1, len(all_times)+1)

fig, ax = plt.subplots(figsize=(8, 6))

# Comparison: continuous training without fallback
ax.plot(all_cum_times, all_steps, color='black', linestyle='--', linewidth=4)

# Main progress curve (with fallback)
ax.plot(main_times, main_steps, color='#ff3a43', linewidth=4)
# Vertical drop (rollback)
ax.plot(fall_times, fall_steps, color='grey', linestyle=':', linewidth=4, alpha=0.7)
# Horizontal line during timeout period
ax.plot([fall_time, timeout_end], [fallback_step, fallback_step], color='#ffde4b', linewidth=4)
# Horizontal line during scheduling period
ax.plot([timeout_end, scheduling_end], [fallback_step, fallback_step], color='#6788e8', linewidth=4)
# Horizontal line during reboot period
ax.plot([scheduling_end, delay_time], [fallback_step, fallback_step], color='mediumseagreen', linewidth=4)
# Continue after delay (all steps 51-95)
ax.plot(extra_curve_times, extra_curve_steps, color='#ff3a43', linewidth=4)

# Mark failure point at step 75
ax.plot(fall_time, 75, 'ro', markersize=15, markeredgecolor='black', markeredgewidth=2)
ax.annotate('Failure\nHappen', xy=(fall_time - 0.5, 75), xytext=(fall_time - 10, 65),
            arrowprops=dict(arrowstyle='->', color='red', lw=2), 
            color='red', fontsize=18, ha='center', weight='bold')

# Calculate time difference at step 80
step_80_index = 79  # 0-indexed, so step 80 is at index 79
perfect_time_at_80 = all_cum_times[step_80_index]
failure_time_at_80 = extra_curve_times[step_80_index - 50]  # Adjust for fallback to step 50
time_diff = failure_time_at_80 - perfect_time_at_80

# Create double arrow using FancyArrowPatch
arrow = FancyArrowPatch((perfect_time_at_80 + 1, 80), (failure_time_at_80 - 1, 80),
                       arrowstyle='<->', mutation_scale=20, 
                       color='black', linewidth=3)
ax.add_patch(arrow)

# Add annotation for time difference
ax.annotate(f'Time Loss\nAfter Failure:\n{time_diff:.1f}min', 
            xy=(perfect_time_at_80 + time_diff/2, 80), 
            xytext=(perfect_time_at_80 + time_diff/2, 80 - 18),
            arrowprops=dict(arrowstyle='->', color='black', lw=2), 
            color='black', fontsize=20, ha='center', weight='bold')

# Annotations
ax.annotate('Unsaved\nProgress', xy=(fall_time, 62.5), xytext=(fall_time+7, 53),
            arrowprops=dict(arrowstyle='->', color='black', lw=2), color='black', fontsize=18, ha='center')

ax.annotate('Timeout\n4.5min', xy=(fall_time+timeout_duration/2, fallback_step), xytext=(fall_time+timeout_duration/2 - 2, fallback_step-15),
            arrowprops=dict(arrowstyle='->', color='black', lw=2), color='black', fontsize=18, ha='center')
ax.annotate('Stop\nand\nReschedule\n15.58min', xy=(timeout_end+scheduling_duration/2, fallback_step), xytext=(timeout_end+scheduling_duration/2, fallback_step-19),
            arrowprops=dict(arrowstyle='->', color='black', lw=2), color='black', fontsize=18, ha='center')
ax.annotate('Restart\n2.5min', xy=(scheduling_end+reboot_duration/2, fallback_step), xytext=(scheduling_end+reboot_duration/2 + 2, fallback_step-15),
            arrowprops=dict(arrowstyle='->', color='black', lw=2), color='black', fontsize=18, ha='center')

# Axis labels
ax.set_xlabel('Training Time (minutes)', fontsize=18)
ax.set_ylabel('Training Step', fontsize=18)

ax.grid(True, linestyle='--', alpha=0.7)
ax.tick_params(axis='both', which='major', labelsize=18)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(30, 87)
ax.set_xlim(0, 45)

plt.tight_layout()
plt.savefig('training_progress_with_failure.pdf', dpi=300, bbox_inches='tight')
plt.show()
