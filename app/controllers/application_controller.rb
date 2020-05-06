class ApplicationController < ActionController::Base
  def landing
  end

  def around_the_internet
    @ls = {}
    
    @ls['Good learning resoures'] = %w(
      http://tokipona.org/
      http://www.tokipona.net/
      https://rnd.neocities.org/tokipona
      https://github.com/stefichjo/toki-pona
      https://tokipona.fandom.com/wiki/lipu_lawa
    )

    @ls['Dictionaries'] = %w(
      http://tokipona.net/tp/ClassicWordList.aspx
      https://docs.google.com/document/d/10hP3kR7mFN0E6xW3U6fZyDf7xKEEvxssM96qLq4E0ms/edit
    )

    @ls['Fonts'] = %w(
      https://github.com/janSame/linja-pona 
      https://github.com/davidar/linja-pona 
    )

    @ls['Active communities'] = %w(
      https://discord.gg/XKzj3ex
      https://reddit.com/r/tokipona
    )

    @ls['Fun and humor'] = %w(
      https://reddit.com/r/mi_lon
    )
  end
end
