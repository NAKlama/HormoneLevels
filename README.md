# HormoneLevels
Compute and graph hormone levels for transgender HRT

## Current state of development

Since I'm developing this software's features as I need them, it is currently only for
transfeminine HRT. It can graph the amount of estradiol valerate inside the body, and
using that, and the lab results at certain points, a conversion factor to calculate the
blood levels from the amount of the ester in the body is calculated, by taking the
average of the ratio between lab tests and calculated hormone in the body.

The confidence interval is calculated taking the square sum residuals between the
resulting blood level curve, and the actual lab tests, and calculating the standard
deviation.

## Planned features

  
  - Graphing of long term fitting with known labs to detect shifts in metabolism
    - Ways to adjust for these
  - Different HRT options
    - Different Estradiol Esters
    - Testosterone Esters
    - Different methods of delivery
    
## Implemented features

  - Calculate and plot blood level estimations from known levels at certain points

## Contributing

I'd love for some transmasculine folk to get in touch with me, and provide me with
the names and half-lifes of commonly used testosterone esters, so I can add them to
the project. You can also add them as an issue as an easy way to ask for certain
hormone esters to be added.

Of course, feel free to create the files for that yourself, and make a pull-request.
I'd be happy to collaborate with someone implementing some cool additional features.

## Disclaimer

I am not a medical professional. The values estimated from this software should not
be used to make medical decisions, without verification by actual blood tests.
I did however study chemistry, have a good knowledge and experience in pharmakinetics,
and software modelling.
This software is intended to give you a better feeling of where your hormone levels
probably are, and is not intended to replace blood tests. In fact, it relies on blood
tests to improve its estimations.