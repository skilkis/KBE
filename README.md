    # KBE
    Utilizing ParaPy to Frontload Preliminary UAV Design

	This file explains the steps required to operate small UAV sizing Knowledge Based Engineering Application. After
	instantiated the main class myUAV please refer to our documentation by firing the ‘open_documentation’
	attribute in the root ‘mainUAV’ class.

        [1.]	Fill in the ‘userinput.xls’ file with the desired mission requirements. This file is in the root/user
        folder. (Filling in the input sheet is optional, as the design parameters can be edited in the ParaPy property
        grid and there are default values.)

        [2.]	Open the ‘main.py’ file in the root folder in PyCharm and run the script. Please wait for the ParaPy GUI
        to open. The CAD viewport will be empty and the product tree will be as shown in the left figure below. The
        right figure shows the property grid, containing inputs, attributes and Parts.

        [3.]	Navigate to the attribute named ‘get_userinput’ in the root level ‘myUAV’ class to load the mission
        requirements set in the previous step (This step is also optional. If this step is skipped, a UAV is created
        from the default values for all design variables.).

        [4.]	Double left click on the ‘myUAV’ root class to create the UAV.

        [5.]	Next, YOU MUST double left click on the attribute ‘final_cg’ in the root level ‘myUAV’ class.
        This will converge the tail sizing with the center of gravity. A plot of the center of gravity convergence will
        appear in the PyCharm IDE.

        [6.]    Next you may browse through all ‘Parts’ of the product tree to see the UAV design. These parts include
        the main wing design, the longitudinal stability parameters, center of gravity position in 3D,
        the horizontal and vertical tails, EOIR payload, fuselage and boom structure design, motor and propeller choice,
        battery sizing and electronics locations. If the hidden attribute is changed to false in the ‘Fuselage’ part,
        the internal components may be seen.

        [7.]	The performance of the UAV is evaluated in the ‘Performance’ part. Here, if the ‘plot_airspeed_vs_power’
        attribute is fired, all power components are plotted against flight velocity. The CD0 used in these calculations
         is calculated using the final wetted areas extracted from ParaPy. The maximum range and endurance speeds are
         extracted and the final mission requirements are recalculated and shown in the plot’s legend.

        [8.]	The relevant UAV design parameters may be exported to the ‘output.xls’ file in the root/user/results
        folder by firing the ‘write_excel’ attribute in the root ‘mainUAV’ Class.

        [9.]	The ‘.stp’ file can be exported by firing the ‘write_step’ attribute in the root ‘mainUAV’ Class.
        This file is in the root/user/model folder.

        [10.]	If desired, one may change design variables, BUT YOU MUST invalidate the attribute from step 5 and then
        re-fire it. This is due to the lazy evaluation of ParaPy and the new CG must converge again with the horizontal
        tail size. Only after this, are the performance results consistent.

        [11.]	Enjoy! And if there are any questions regarding the app do not hesitate to ask!
